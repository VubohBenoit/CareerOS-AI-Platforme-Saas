#!/usr/bin/env python3
"""
DeafHire — WLASL Full Dataset Downloader
=========================================
Télécharge l'intégralité du dataset WLASL (Word-Level American Sign Language)
— 2 000 signes, ~21 000 vidéos YouTube — extrait les landmarks MediaPipe
et génère le dataset JSON compatible avec train_large.py.

IMPORTANT : WLASL est en ASL (American Sign Language), pas en LSF.
Les noms de classes dans le modèle entraîné seront en anglais (glosses ASL).

Source  : https://github.com/dxli94/WLASL
Dataset : WLASL_v0.3.json (2000 signes, ~21 000 vidéos)

Prérequis :
  pip install yt-dlp mediapipe opencv-python numpy requests

Usage :
  python download_wlasl.py all                   # tout (télécharge + extrait)
  python download_wlasl.py download              # télécharge les vidéos seulement
  python download_wlasl.py download --top 100    # les 100 signes les plus fréquents
  python download_wlasl.py download --gloss hello yes no  # signes spécifiques
  python download_wlasl.py extract               # extrait les landmarks
  python download_wlasl.py stats                 # stats du dataset courant
  python download_wlasl.py list-glosses          # liste tous les 2000 signes
  python download_wlasl.py train                 # lance train_large.py sur dataset_wlasl.json

Ordre de grandeur (connexion normale) :
  100 signes × 10 vidéos : ~2–3 h téléchargement, ~1 h extraction, ~10 min entraînement
  500 signes × 10 vidéos : ~8–12 h téléchargement, ~4 h extraction, ~30 min entraînement
  2000 signes             : plusieurs jours — utiliser --jobs 4 pour paralléliser
"""

import argparse
import concurrent.futures
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

for mod, pkg in [("cv2","opencv-python"), ("mediapipe","mediapipe"),
                 ("numpy","numpy"), ("requests","requests")]:
    try:
        __import__(mod)
    except ImportError:
        sys.exit(f"❌  {pkg} manquant : pip install {pkg}")

import cv2
import mediapipe as mp
import numpy as np
import requests

# ── Chemins ───────────────────────────────────────────────────────────────
ROOT_DIR    = Path(__file__).parent.parent
VIDEOS_DIR  = ROOT_DIR / "data" / "wlasl_videos"
DATASET_OUT = ROOT_DIR / "data" / "dataset_wlasl.json"
META_CACHE  = ROOT_DIR / "data" / "wlasl_meta.json"

WLASL_JSON_URL = (
    "https://raw.githubusercontent.com/dxli94/WLASL/"
    "master/start_kit/WLASL_v0.3.json"
)

MIN_SAMPLES = 10


# ── Métadonnées WLASL ──────────────────────────────────────────────────────
def fetch_meta() -> list:
    if META_CACHE.exists():
        with open(META_CACHE, encoding="utf-8") as f:
            data = json.load(f)
        print(f"  Métadonnées WLASL chargées depuis le cache — {len(data)} signes")
        return data

    print("  Téléchargement des métadonnées WLASL (GitHub)…")
    META_CACHE.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = requests.get(WLASL_JSON_URL, timeout=30)
        r.raise_for_status()
        data = r.json()
        with open(META_CACHE, "w", encoding="utf-8") as f:
            json.dump(data, f)
        print(f"  ✅  {len(data)} signes — mis en cache ({META_CACHE.name})")
        return data
    except Exception as e:
        sys.exit(f"❌  Impossible de télécharger les métadonnées WLASL : {e}")


def select_glosses(meta: list, top: int | None, glosses: list | None) -> list:
    """Retourne les entrées WLASL filtrées selon les options CLI."""
    if glosses:
        low = {g.lower() for g in glosses}
        return [e for e in meta if e["gloss"].lower() in low]
    if top:
        # Trie par nombre d'instances décroissant, garde les N premiers
        return sorted(meta, key=lambda e: len(e["instances"]), reverse=True)[:top]
    return meta


# ── Téléchargement vidéo ──────────────────────────────────────────────────
def _safe_name(gloss: str) -> str:
    return (gloss.replace(" ", "_").replace("/", "_")
                 .replace("'", "").replace('"', "")
                 .replace("(", "").replace(")", ""))


def download_one(url: str, out_path: Path) -> bool:
    if out_path.exists() and out_path.stat().st_size > 10_000:
        return True
    cmd = [
        "yt-dlp", url,
        "--format", "best[height<=480][ext=mp4]/best[height<=480]/best",
        "--output", str(out_path),
        "--no-playlist", "--quiet", "--no-warnings",
        "--no-check-certificate",
        "--extractor-args", "youtube:player_client=android",
        "--socket-timeout", "20",
        "--retries", "2",
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if out_path.exists() and out_path.stat().st_size > 10_000:
            return True
        for p in out_path.parent.glob(out_path.stem + ".*"):
            if p.stat().st_size > 10_000:
                p.rename(out_path)
                return True
    except Exception:
        pass
    return False


def download_sign(entry: dict, max_videos: int) -> tuple[str, int]:
    gloss     = entry["gloss"]
    instances = [i for i in entry["instances"]
                 if i.get("source") == "youtube"
                 and i.get("url")]

    if not instances:
        return gloss, 0

    sign_dir = VIDEOS_DIR / _safe_name(gloss)
    sign_dir.mkdir(parents=True, exist_ok=True)

    ok = 0
    for inst in instances[:max_videos]:
        vid_id = inst.get("video_id", f"v{ok}")
        out    = sign_dir / f"{vid_id}.mp4"
        if download_one(inst["url"], out):
            ok += 1
    return gloss, ok


# ── Normalisation MediaPipe ────────────────────────────────────────────────
def norm_hand(hand_lm):
    if hand_lm is None:
        return [0.0] * 63
    pts = [(lm.x, lm.y, lm.z) for lm in hand_lm.landmark]
    wx, wy, wz = pts[0]
    rx, ry, rz = pts[9]
    scale = math.sqrt((rx-wx)**2 + (ry-wy)**2 + (rz-wz)**2) or 1e-6
    return [(c - o) / scale
            for x, y, z in pts
            for c, o in [(x, wx), (y, wy), (z, wz)]]


def extract_features(results):
    return norm_hand(results.right_hand_landmarks) + norm_hand(results.left_hand_landmarks)


def has_hand(results) -> bool:
    return (results.right_hand_landmarks is not None or
            results.left_hand_landmarks  is not None)


def augment(feat: list, n: int) -> list:
    arr      = np.array(feat, dtype=np.float32)
    variants = [feat]
    for _ in range(n):
        noise = np.random.normal(0, 0.020, arr.shape).astype(np.float32)
        scale = np.random.uniform(0.88, 1.12)
        variants.append((arr * scale + noise).tolist())
    return variants


def extract_video(vp: Path, holistic, skip: int, aug_n: int) -> list:
    cap = cv2.VideoCapture(str(vp))
    if not cap.isOpened():
        return []
    samples, idx = [], 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        idx += 1
        if idx % skip:
            continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = holistic.process(rgb)
        if has_hand(res):
            samples.extend(augment(extract_features(res), aug_n))
    cap.release()
    return samples


# ── Dataset I/O ───────────────────────────────────────────────────────────
def load_dataset(path: Path) -> dict:
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_dataset(dataset: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False)


def print_stats(dataset: dict):
    if not dataset:
        print("Dataset vide.")
        return
    total   = sum(len(v) for v in dataset.values())
    ready   = sum(1 for v in dataset.values() if len(v) >= MIN_SAMPLES)
    print(f"\n  {len(dataset)} signes dans le dataset")
    print(f"  {ready} signes avec ≥ {MIN_SAMPLES} exemples (prêts pour l'entraînement)")
    print(f"  {total} exemples au total")

    # Top 10 + bottom 10
    sorted_signs = sorted(dataset.items(), key=lambda x: len(x[1]), reverse=True)
    print(f"\n  Top 10 :")
    for g, v in sorted_signs[:10]:
        bar = "█" * min(len(v) // 50, 20)
        print(f"    {g:<25} {len(v):>5}  {bar}")
    if len(sorted_signs) > 20:
        print(f"\n  Bottom 10 :")
        for g, v in sorted_signs[-10:]:
            bar = "█" * min(len(v) // 50, 20)
            ok  = "✓" if len(v) >= MIN_SAMPLES else "✗"
            print(f"  {ok} {g:<25} {len(v):>5}  {bar}")
    print()


# ── Commandes ─────────────────────────────────────────────────────────────
def cmd_list_glosses(args):
    meta = fetch_meta()
    meta_sorted = sorted(meta, key=lambda e: e["gloss"])
    print(f"\n  {len(meta)} signes WLASL disponibles :\n")
    for i, e in enumerate(meta_sorted):
        n_yt = sum(1 for inst in e["instances"] if inst.get("source") == "youtube")
        print(f"  {i+1:>4}. {e['gloss']:<30}  {n_yt:>3} vidéos YouTube")
    print()


def cmd_download(args):
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        sys.exit("❌  yt-dlp manquant : pip install yt-dlp")

    meta    = fetch_meta()
    entries = select_glosses(meta, args.top, args.gloss)
    total   = len(entries)

    print(f"\n  {total} signes à télécharger ({args.max_videos} vidéos max / signe)")
    print(f"  Jobs parallèles : {args.jobs}\n")

    done = 0

    def _worker(entry):
        return download_sign(entry, args.max_videos)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(_worker, e): e["gloss"] for e in entries}
        for fut in concurrent.futures.as_completed(futures):
            gloss, ok = fut.result()
            done += 1
            print(f"  [{done}/{total}] {gloss:<28} {ok} vidéos téléchargées")

    print(f"\n  Téléchargement terminé — vidéos dans {VIDEOS_DIR}\n")


def cmd_extract(args):
    holistic = mp.solutions.holistic.Holistic(
        static_image_mode=False, model_complexity=1,
        min_detection_confidence=0.5, min_tracking_confidence=0.5,
    )
    dataset = load_dataset(DATASET_OUT)

    sign_dirs = sorted(VIDEOS_DIR.iterdir()) if VIDEOS_DIR.exists() else []
    if not sign_dirs:
        print(f"  Aucune vidéo dans {VIDEOS_DIR} — lancez d'abord 'download'")
        holistic.close()
        return

    total = len(sign_dirs)
    for i, sign_dir in enumerate(sign_dirs):
        if not sign_dir.is_dir():
            continue

        gloss  = sign_dir.name.replace("_", " ")
        videos = list(sign_dir.glob("*.mp4"))
        if not videos:
            continue

        if gloss in dataset and len(dataset[gloss]) >= args.max_samples and not args.force:
            print(f"  [{i+1}/{total}] {gloss:<28} déjà {len(dataset[gloss])} ex — skip")
            continue

        print(f"  [{i+1}/{total}] {gloss:<28} ({len(videos)} vidéos)  ", end="", flush=True)
        all_samples = []

        for vp in videos:
            samples = extract_video(vp, holistic, args.skip, args.augment)
            all_samples.extend(samples)
            if len(all_samples) >= args.max_samples:
                break

        all_samples = all_samples[:args.max_samples]
        if all_samples:
            dataset[gloss] = all_samples
            print(f"{len(all_samples)} exemples")
        else:
            print("0 main détectée")

        # Sauvegarde incrémentale toutes les 10 classes
        if i % 10 == 0:
            save_dataset(dataset, DATASET_OUT)

    holistic.close()
    save_dataset(dataset, DATASET_OUT)
    print_stats(dataset)


def cmd_all(args):
    cmd_download(args)
    cmd_extract(args)


def cmd_stats(args):
    dataset = load_dataset(DATASET_OUT)
    print_stats(dataset)


def cmd_train(args):
    train_script = Path(__file__).parent / "train_large.py"
    cmd = [
        sys.executable, str(train_script),
        "--data", str(DATASET_OUT),
        "--min-samples", str(MIN_SAMPLES),
    ]
    print(f"  Lancement : {' '.join(str(c) for c in cmd)}\n")
    subprocess.run(cmd)


# ── Main ──────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="DeafHire — WLASL full dataset downloader + extractor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--skip",        type=int,   default=3,
                        help="Traiter 1 frame sur N (défaut: 3)")
    common.add_argument("--augment",     type=int,   default=5,
                        help="Variantes augmentées par frame (défaut: 5)")
    common.add_argument("--max-samples", type=int,   default=2000,
                        help="Exemples max par signe pour l'extraction (défaut: 2000)")
    common.add_argument("--max-videos",  type=int,   default=15,
                        help="Vidéos max à télécharger par signe (défaut: 15)")
    common.add_argument("--jobs",        type=int,   default=3,
                        help="Téléchargements en parallèle (défaut: 3)")
    common.add_argument("--top",         type=int,   default=None,
                        help="Limiter aux N signes les plus fréquents (ex: --top 500)")
    common.add_argument("--gloss",       nargs="+",  default=None,
                        help="Signes spécifiques (ex: --gloss hello yes no)")
    common.add_argument("--force",       action="store_true",
                        help="Ré-extraire même si déjà dans le dataset")

    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("all",          parents=[common], help="Télécharger + extraire tout")
    sub.add_parser("download",     parents=[common], help="Télécharger les vidéos")
    sub.add_parser("extract",      parents=[common], help="Extraire les landmarks")
    sub.add_parser("stats",                          help="Stats du dataset courant")
    sub.add_parser("list-glosses",                   help="Lister les 2000 signes WLASL")
    sub.add_parser("train",                          help="Lancer l'entraînement sur dataset_wlasl.json")

    args = parser.parse_args()
    {
        "all":          cmd_all,
        "download":     cmd_download,
        "extract":      cmd_extract,
        "stats":        cmd_stats,
        "list-glosses": cmd_list_glosses,
        "train":        cmd_train,
    }[args.cmd](args)


if __name__ == "__main__":
    main()
