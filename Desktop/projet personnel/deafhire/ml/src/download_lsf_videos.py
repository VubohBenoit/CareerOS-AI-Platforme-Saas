#!/usr/bin/env python3
"""
DeafHire — Téléchargeur de vidéos LSF via YouTube
==================================================
Télécharge automatiquement des vidéos de démonstration LSF depuis YouTube
pour chaque signe du vocabulaire, puis extrait les landmarks MediaPipe
pour générer un dataset JSON importable dans le trainer navigateur.

Prérequis :
  pip install yt-dlp mediapipe opencv-python numpy

Usage :
  # Télécharger + extraire tous les signes
  python download_lsf_videos.py all

  # Un signe spécifique
  python download_lsf_videos.py sign "Bonjour"

  # Seulement extraire les landmarks (si vidéos déjà téléchargées)
  python download_lsf_videos.py extract

  # Voir les stats du dataset généré
  python download_lsf_videos.py stats
"""

import argparse
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

# ── Vérification des dépendances ──────────────────────────────────────────
def check_dep(module, pip_name):
    try:
        __import__(module)
    except ImportError:
        sys.exit(f"❌  {pip_name} manquant : pip install {pip_name}")

check_dep("cv2",       "opencv-python")
check_dep("mediapipe", "mediapipe")
check_dep("numpy",     "numpy")

import cv2
import mediapipe as mp
import numpy as np

def check_ytdlp():
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        sys.exit("❌  yt-dlp manquant : pip install yt-dlp  (ou brew install yt-dlp)")

# ── Configuration ─────────────────────────────────────────────────────────
CLASSES = [
    "Bonjour", "Merci", "Oui", "Non", "Je / Moi",
    "Travail", "Expérience", "Formation", "Comprendre",
    "Répéter", "Question", "Compétence", "Équipe", "Futur",
]

MIN_SAMPLES = 10

# Requêtes YouTube pour chaque signe — plusieurs variantes pour maximiser
# les chances de trouver une démonstration claire.
SEARCH_QUERIES = {
    "Bonjour":    ["bonjour langue des signes française LSF",
                   "LSF bonjour signe tutoriel"],
    "Merci":      ["merci LSF langue des signes française",
                   "signe merci LSF tutoriel"],
    "Oui":        ["oui LSF langue des signes française",
                   "signe oui LSF"],
    "Non":        ["non LSF langue des signes française",
                   "signe non LSF tutoriel"],
    "Je / Moi":   ["je moi LSF langue des signes",
                   "signe je moi LSF français"],
    "Travail":    ["travail LSF langue des signes française",
                   "signe travail LSF"],
    "Expérience": ["expérience LSF langue des signes",
                   "signe expérience LSF"],
    "Formation":  ["formation LSF langue des signes",
                   "signe formation LSF"],
    "Comprendre": ["comprendre LSF langue des signes",
                   "signe comprendre LSF"],
    "Répéter":    ["répéter LSF langue des signes",
                   "signe répéter recommencer LSF"],
    "Question":   ["question LSF langue des signes",
                   "signe question LSF"],
    "Compétence": ["compétence LSF langue des signes",
                   "signe compétence LSF"],
    "Équipe":     ["équipe LSF langue des signes",
                   "signe équipe groupe LSF"],
    "Futur":      ["futur avenir LSF langue des signes",
                   "signe futur LSF"],
}

# ── Chemins ───────────────────────────────────────────────────────────────
ROOT_DIR    = Path(__file__).parent.parent
VIDEOS_DIR  = ROOT_DIR / "data" / "videos"
DATASET_OUT = ROOT_DIR / "data" / "dataset_lsf.json"


# ── Normalisation (identique à SignTrainer.extract en JS) ─────────────────
def norm_hand(hand_lm):
    if hand_lm is None:
        return [0.0] * 63
    pts = [(lm.x, lm.y, lm.z) for lm in hand_lm.landmark]
    wx, wy, wz = pts[0]
    rx, ry, rz = pts[9]
    scale = math.sqrt((rx - wx)**2 + (ry - wy)**2 + (rz - wz)**2) or 1e-6
    out = []
    for x, y, z in pts:
        out += [(x - wx) / scale, (y - wy) / scale, (z - wz) / scale]
    return out


def extract_features(results):
    return norm_hand(results.right_hand_landmarks) + norm_hand(results.left_hand_landmarks)


def has_hand(results):
    return (results.right_hand_landmarks is not None or
            results.left_hand_landmarks  is not None)


def augment(feat, n=5):
    arr = np.array(feat, dtype=np.float32)
    variants = [feat]
    for _ in range(n):
        noise = np.random.normal(0, 0.022, arr.shape).astype(np.float32)
        scale = np.random.uniform(0.90, 1.10)
        variants.append((arr * scale + noise).tolist())
    return variants


# ── Téléchargement via yt-dlp ─────────────────────────────────────────────
def download_video(sign: str, out_dir: Path, max_duration: int = 120):
    """
    Télécharge la première vidéo correspondant aux requêtes de recherche
    pour ce signe. Retourne le chemin du fichier vidéo ou None si échec.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_name = sign.replace(" / ", "_").replace(" ", "_").replace("é", "e").replace("è", "e").replace("ê", "e").replace("à", "a").replace("ç", "c")
    out_path  = out_dir / f"{safe_name}.mp4"

    if out_path.exists():
        print(f"  ✓ Déjà téléchargé : {out_path.name}")
        return out_path

    queries = SEARCH_QUERIES.get(sign, [f"LSF {sign} langue des signes"])

    for query in queries:
        print(f"  🔍 Recherche : {query}")
        cmd = [
            "yt-dlp",
            f"ytsearch1:{query}",
            "--format",  "best[height<=480]/best",
            "--output",  str(out_path),
            "--no-playlist",
            "--quiet",
            "--no-warnings",
            "--no-check-certificate",
            "--extractor-args", "youtube:player_client=android",   # contourne le 403
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            # yt-dlp peut nommer le fichier différemment si plusieurs résultats
            # cherche tout fichier vidéo dans le dossier correspondant au signe
            candidates = sorted(out_dir.glob(f"{safe_name}*.mp4"),
                                 key=lambda p: p.stat().st_size, reverse=True)
            if not candidates:
                candidates = sorted(out_dir.glob(f"{safe_name}*"),
                                    key=lambda p: p.stat().st_size, reverse=True)
            if candidates and candidates[0].stat().st_size > 10_000:
                best = candidates[0]
                if best != out_path:
                    best.rename(out_path)
                print(f"  ✅ Téléchargé : {out_path.name}")
                return out_path
            # Affiche stderr pour diagnostic si l'échec persiste
            if result.stderr:
                print(f"  ℹ  {result.stderr.strip()[:120]}")
        except subprocess.TimeoutExpired:
            print(f"  ⚠️  Timeout sur : {query}")
        except Exception as e:
            print(f"  ⚠️  Erreur : {e}")

    print(f"  ❌ Aucune vidéo trouvée pour '{sign}'")
    return None


# ── Extraction de landmarks depuis une vidéo ─────────────────────────────
def extract_from_video(video_path: Path, sign: str, holistic,
                       skip: int = 3, augment_n: int = 5) -> list:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"  ❌ Impossible d'ouvrir : {video_path}")
        return []

    total   = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    samples = []
    idx     = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        idx += 1
        if idx % skip != 0:
            continue

        pct = int(idx / total * 100)
        print(f"\r    Extraction {pct}%  ({len(samples)} landmarks)", end="", flush=True)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = holistic.process(rgb)
        if has_hand(res):
            feat = extract_features(res)
            samples.extend(augment(feat, augment_n))

    cap.release()
    print()
    return samples


# ── Dataset I/O ──────────────────────────────────────────────────────────
def load_dataset(path: Path) -> dict:
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_dataset(dataset: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False)
    total = sum(len(v) for v in dataset.values())
    print(f"\n✅  Dataset sauvegardé → {path}")
    print(f"    {total} exemples au total\n")


def print_stats(dataset: dict):
    print(f"\n{'Signe':<22} {'Exemples':>9}")
    print("─" * 34)
    total = 0
    for sign in CLASSES:
        n = len(dataset.get(sign, []))
        total += n
        ok = "✓" if n >= MIN_SAMPLES else "·"
        bar = "█" * min(n // 10, 20) + "░" * max(0, 20 - n // 10)
        print(f"  {ok} {sign:<20} {n:>5}  {bar}")
    print("─" * 34)
    print(f"    {'TOTAL':<20} {total:>5}\n")
    print("→ Importez dataset_lsf.json dans le trainer navigateur")
    print("  (bouton IA → Importer dans la page d'entretien)\n")


# ── Commandes ────────────────────────────────────────────────────────────
def cmd_all(args):
    check_ytdlp()
    holistic = mp.solutions.holistic.Holistic(
        static_image_mode=False, model_complexity=1,
        min_detection_confidence=0.5, min_tracking_confidence=0.5,
    )
    dataset = load_dataset(DATASET_OUT)

    for sign in CLASSES:
        if sign in dataset and len(dataset[sign]) >= MIN_SAMPLES and not args.force:
            print(f"\n[{sign}] déjà {len(dataset[sign])} exemples — passer (--force pour ré-extraire)")
            continue

        print(f"\n{'─' * 50}")
        print(f"  {sign}")
        print('─' * 50)

        video_path = download_video(sign, VIDEOS_DIR)
        if video_path is None:
            continue

        samples = extract_from_video(video_path, sign, holistic,
                                     skip=args.skip, augment_n=args.augment)
        if samples:
            dataset[sign] = samples
            print(f"  → {len(samples)} exemples extraits pour '{sign}'")
            save_dataset(dataset, DATASET_OUT)   # sauvegarde incrémentale
        else:
            print(f"  ⚠️  Aucun landmark extrait pour '{sign}'")

    holistic.close()
    print_stats(dataset)


def cmd_sign(args):
    check_ytdlp()
    holistic = mp.solutions.holistic.Holistic(
        static_image_mode=False, model_complexity=1,
        min_detection_confidence=0.5, min_tracking_confidence=0.5,
    )
    dataset = load_dataset(DATASET_OUT)

    sign       = args.sign
    video_path = download_video(sign, VIDEOS_DIR)
    if video_path:
        samples = extract_from_video(video_path, sign, holistic,
                                     skip=args.skip, augment_n=args.augment)
        if samples:
            dataset[sign] = samples
            save_dataset(dataset, DATASET_OUT)
            print_stats(dataset)
        else:
            print(f"⚠️  Aucun landmark extrait pour '{sign}'")

    holistic.close()


def cmd_extract(args):
    """Extrait les landmarks de toutes les vidéos déjà téléchargées."""
    holistic = mp.solutions.holistic.Holistic(
        static_image_mode=False, model_complexity=1,
        min_detection_confidence=0.5, min_tracking_confidence=0.5,
    )
    dataset = {}

    for sign in CLASSES:
        safe_name = sign.replace(" / ", "_").replace(" ", "_").replace("é", "e").replace("è", "e").replace("ê", "e").replace("à", "a").replace("ç", "c")
        video_path = VIDEOS_DIR / f"{safe_name}.mp4"

        if not video_path.exists():
            print(f"  · {sign} — pas de vidéo ({video_path.name})")
            continue

        print(f"\n  ► {sign}")
        samples = extract_from_video(video_path, sign, holistic,
                                     skip=args.skip, augment_n=args.augment)
        if samples:
            dataset[sign] = samples
            print(f"    {len(samples)} exemples extraits")

    holistic.close()
    save_dataset(dataset, DATASET_OUT)
    print_stats(dataset)


def cmd_stats(args):
    dataset = load_dataset(DATASET_OUT)
    if not dataset:
        print(f"Aucun dataset trouvé à : {DATASET_OUT}")
        return
    print_stats(dataset)


# ── Main ─────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="DeafHire — Téléchargeur de vidéos LSF + extracteur de landmarks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--skip",    type=int, default=4,
                        help="Traiter 1 frame sur N (défaut: 4)")
    common.add_argument("--augment", type=int, default=5,
                        help="Variantes augmentées par frame (défaut: 5)")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_all = sub.add_parser("all", parents=[common],
                            help="Télécharger + extraire tous les signes")
    p_all.add_argument("--force", action="store_true",
                       help="Ré-extraire même si déjà présent dans le dataset")

    p_sign = sub.add_parser("sign", parents=[common],
                             help="Télécharger + extraire un signe spécifique")
    p_sign.add_argument("sign", choices=CLASSES, metavar="SIGNE")

    p_ext = sub.add_parser("extract", parents=[common],
                            help="Extraire les landmarks des vidéos déjà téléchargées")

    sub.add_parser("stats", help="Afficher les statistiques du dataset généré")

    args = parser.parse_args()

    dispatch = {
        "all":     cmd_all,
        "sign":    cmd_sign,
        "extract": cmd_extract,
        "stats":   cmd_stats,
    }
    dispatch[args.cmd](args)


if __name__ == "__main__":
    main()
