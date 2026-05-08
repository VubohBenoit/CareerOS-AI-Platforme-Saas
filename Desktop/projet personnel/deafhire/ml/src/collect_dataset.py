#!/usr/bin/env python3
"""
DeafHire — Dataset Collector (JSON, compatible browser trainer)
==============================================================
Collecte des landmarks MediaPipe depuis la webcam, des vidéos ou des dossiers
d'images et génère un JSON directement importable dans le trainer navigateur.

Normalisation identique à SignTrainer.extract() (JS) :
  • Origine    → poignet (landmark 0)
  • Échelle    → distance poignet → MCP majeur (landmark 9)
  • Sortie     → vecteur 126-dim  (21 pts × 3 coords × 2 mains)

Modes :
  webcam   — enregistrement interactif signe par signe
  video    — extraction depuis un fichier vidéo
  images   — extraction depuis un dossier d'images
  stats    — affiche les statistiques d'un fichier JSON
  merge    — fusionne plusieurs fichiers JSON en un seul

Usage :
  python collect_dataset.py webcam --sign "Bonjour" --samples 30
  python collect_dataset.py video  --sign "Merci"   --input video.mp4
  python collect_dataset.py images --sign "Oui"     --input ./photos/oui/
  python collect_dataset.py stats  dataset.json
  python collect_dataset.py merge  a.json b.json --output merged.json
"""

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

# ── Vérification des dépendances ────────────────────────────────────────────
try:
    import cv2
except ImportError:
    sys.exit("❌  opencv-python manquant : pip install opencv-python")

try:
    import mediapipe as mp
except ImportError:
    sys.exit("❌  mediapipe manquant : pip install mediapipe")

try:
    import numpy as np
except ImportError:
    sys.exit("❌  numpy manquant : pip install numpy")

# ── Signes disponibles (même ordre que SignTrainer.CLASSES) ────────────────
CLASSES = [
    "Bonjour", "Merci", "Oui", "Non", "Je / Moi",
    "Travail", "Expérience", "Formation", "Comprendre",
    "Répéter", "Question", "Compétence", "Équipe", "Futur",
]

MIN_SAMPLES = 10   # seuil minimum pour entraîner


# ── Normalisation (miroir exact de SignTrainer.extract en JS) ───────────────
def _norm_hand(landmarks_21):
    """
    Normalise une main :
      - Origine → poignet (index 0)
      - Échelle → dist(poignet, MCP majeur index 9)
    Retourne liste 63-dim. Si pas de main détectée → liste de 0.
    """
    if landmarks_21 is None:
        return [0.0] * 63
    pts = [(lm.x, lm.y, lm.z) for lm in landmarks_21.landmark]
    wx, wy, wz = pts[0]
    rx, ry, rz = pts[9]
    scale = math.sqrt((rx - wx) ** 2 + (ry - wy) ** 2 + (rz - wz) ** 2) or 1e-6
    out = []
    for x, y, z in pts:
        out += [(x - wx) / scale, (y - wy) / scale, (z - wz) / scale]
    return out


def extract_features(results):
    """Retourne vecteur 126-dim depuis les résultats MediaPipe Holistic."""
    right = _norm_hand(results.right_hand_landmarks)
    left  = _norm_hand(results.left_hand_landmarks)
    return right + left   # 63 + 63 = 126


def has_hand(results):
    return results.right_hand_landmarks is not None or results.left_hand_landmarks is not None


# ── Augmentation ────────────────────────────────────────────────────────────
def augment(feat, n=7):
    """
    Génère n variantes augmentées d'un vecteur 126-dim.
    Applique : bruit gaussien + jitter d'échelle.
    Garde l'original comme premier élément.
    """
    arr = np.array(feat, dtype=np.float32)
    variants = [feat]
    for _ in range(n):
        noise = np.random.normal(0, 0.025, arr.shape).astype(np.float32)
        scale = np.random.uniform(0.88, 1.12)
        variants.append((arr * scale + noise).tolist())
    return variants


# ── I/O JSON ────────────────────────────────────────────────────────────────
def load_dataset(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_dataset(dataset, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False)
    total = sum(len(v) for v in dataset.values())
    print(f"✅  Sauvegardé → {path}  ({total} exemples au total)")


def print_stats(dataset):
    print(f"\n{'Signe':<22} {'Exemples':>9}  {'OK?':>4}")
    print("─" * 38)
    total = 0
    for sign in CLASSES:
        n = len(dataset.get(sign, []))
        total += n
        ok = "✓" if n >= MIN_SAMPLES else "·"
        bar_n = min(n, MIN_SAMPLES)
        bar = "█" * bar_n + "░" * (MIN_SAMPLES - bar_n)
        print(f"  {ok} {sign:<20} {n:>5}  {bar}")
    print("─" * 38)
    print(f"    {'TOTAL':<20} {total:>5}\n")


# ── MediaPipe setup ─────────────────────────────────────────────────────────
def make_holistic(static=False):
    return mp.solutions.holistic.Holistic(
        static_image_mode=static,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )


# ============================================================
#  MODE WEBCAM — enregistrement interactif
# ============================================================
COUNTDOWN_SEC = 3


def mode_webcam(args):
    sign   = args.sign
    target = args.samples
    output = args.output
    augn   = args.augment

    dataset = load_dataset(output) if args.append else {}
    existing = len(dataset.get(sign, []))
    print(f"\n📷  Webcam — signe : '{sign}'")
    print(f"    Objectif : {target} captures  (existantes : {existing})")
    print(f"    Augmentation ×{augn + 1}  →  {target * (augn + 1)} exemples effectifs")
    print()
    print("    ESPACE  = lancer le compte à rebours et capturer")
    print("    S       = sauvegarder et continuer")
    print("    Q       = sauvegarder et quitter\n")

    holistic = make_holistic(static=False)
    cap      = cv2.VideoCapture(0)
    if not cap.isOpened():
        sys.exit("❌  Impossible d'ouvrir la webcam.")

    captures   = 0
    collecting = False
    countdown  = 0
    t_start    = 0

    mp_draw = mp.solutions.drawing_utils
    mp_style = mp.solutions.drawing_styles

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)   # miroir
        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res   = holistic.process(rgb)

        # Dessine les landmarks
        if res.right_hand_landmarks:
            mp_draw.draw_landmarks(frame, res.right_hand_landmarks,
                                   mp.solutions.holistic.HAND_CONNECTIONS,
                                   mp_style.get_default_hand_landmarks_style(),
                                   mp_style.get_default_hand_connections_style())
        if res.left_hand_landmarks:
            mp_draw.draw_landmarks(frame, res.left_hand_landmarks,
                                   mp.solutions.holistic.HAND_CONNECTIONS,
                                   mp_style.get_default_hand_landmarks_style(),
                                   mp_style.get_default_hand_connections_style())

        h, w = frame.shape[:2]

        # HUD
        cv2.rectangle(frame, (0, 0), (w, 50), (20, 20, 40), -1)
        hand_ok = has_hand(res)
        dot_col = (0, 220, 100) if hand_ok else (60, 60, 80)
        cv2.circle(frame, (w - 20, 25), 8, dot_col, -1)
        cv2.putText(frame,
                    f"Signe : {sign}  |  Capturés : {captures}/{target}",
                    (10, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (220, 220, 255), 2)

        # Compte à rebours
        if collecting:
            elapsed = time.time() - t_start
            remaining = COUNTDOWN_SEC - elapsed
            if remaining > 0:
                txt = f"{remaining:.1f}s"
                cv2.putText(frame, txt, (w // 2 - 40, h // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 200, 255), 5)
            else:
                # Capture !
                if hand_ok:
                    feat = extract_features(res)
                    if sign not in dataset:
                        dataset[sign] = []
                    dataset[sign].extend(augment(feat, augn))
                    captures += 1
                    print(f"  ✓ Capture {captures}/{target}"
                          f"  ({len(dataset[sign])} exemples)")
                else:
                    print("  ✗ Pas de main détectée — réessayez")
                collecting = False

        cv2.imshow("DeafHire — Collecte webcam", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(" ") and not collecting:
            collecting = True
            t_start    = time.time()

        elif key == ord("s"):
            save_dataset(dataset, output)

        elif key == ord("q") or captures >= target:
            break

    cap.release()
    cv2.destroyAllWindows()
    holistic.close()
    save_dataset(dataset, output)
    print_stats(dataset)


# ============================================================
#  MODE VIDEO — extraction depuis fichier
# ============================================================
def mode_video(args):
    sign   = args.sign
    output = args.output
    augn   = args.augment
    skip   = args.skip

    dataset = load_dataset(output) if args.append else {}
    print(f"\n🎬  Vidéo — signe : '{sign}'  fichier : {args.input}")

    holistic = make_holistic(static=False)
    cap      = cv2.VideoCapture(args.input)
    if not cap.isOpened():
        sys.exit(f"❌  Impossible d'ouvrir : {args.input}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps          = cap.get(cv2.CAP_PROP_FPS) or 25
    raw_samples  = []
    idx          = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        idx += 1
        if idx % skip != 0:
            continue
        pct = int(idx / max(total_frames, 1) * 100)
        print(f"\r  Traitement : {pct}%  ({idx}/{total_frames} frames)", end="", flush=True)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = holistic.process(rgb)
        if has_hand(res):
            raw_samples.append(extract_features(res))

    cap.release()
    holistic.close()
    print()

    if not raw_samples:
        print("⚠️  Aucune main détectée dans la vidéo.")
        return

    if sign not in dataset:
        dataset[sign] = []
    for feat in raw_samples:
        dataset[sign].extend(augment(feat, augn))

    print(f"  {len(raw_samples)} frames → {len(dataset[sign])} exemples (aug ×{augn + 1})")
    save_dataset(dataset, output)
    print_stats(dataset)


# ============================================================
#  MODE IMAGES — extraction depuis dossier
# ============================================================
def mode_images(args):
    sign   = args.sign
    output = args.output
    augn   = args.augment
    exts   = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}

    dataset  = load_dataset(output) if args.append else {}
    img_dir  = Path(args.input)
    if not img_dir.is_dir():
        sys.exit(f"❌  Dossier introuvable : {args.input}")

    files = sorted(f for f in img_dir.iterdir() if f.suffix.lower() in exts)
    print(f"\n🖼️   Images — signe : '{sign}'  dossier : {args.input}  ({len(files)} fichiers)")

    holistic    = make_holistic(static=True)
    raw_samples = []

    for i, fp in enumerate(files):
        img = cv2.imread(str(fp))
        if img is None:
            continue
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        res = holistic.process(rgb)
        if has_hand(res):
            raw_samples.append(extract_features(res))
        print(f"\r  {i + 1}/{len(files)}  ({len(raw_samples)} avec main détectée)", end="", flush=True)

    holistic.close()
    print()

    if not raw_samples:
        print("⚠️  Aucune main détectée dans les images.")
        return

    if sign not in dataset:
        dataset[sign] = []
    for feat in raw_samples:
        dataset[sign].extend(augment(feat, augn))

    print(f"  {len(raw_samples)} images → {len(dataset[sign])} exemples (aug ×{augn + 1})")
    save_dataset(dataset, output)
    print_stats(dataset)


# ============================================================
#  MODE STATS
# ============================================================
def mode_stats(args):
    dataset = load_dataset(args.file)
    print(f"\nDataset : {args.file}")
    print_stats(dataset)


# ============================================================
#  MODE MERGE
# ============================================================
def mode_merge(args):
    merged = {}
    for fp in args.files:
        data = load_dataset(fp)
        for sign, samples in data.items():
            if sign not in merged:
                merged[sign] = []
            merged[sign].extend(samples)
    save_dataset(merged, args.output)
    print_stats(merged)


# ============================================================
#  MAIN
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="DeafHire — Collecte de données de signes LSF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # ── webcam ──
    p_web = sub.add_parser("webcam", help="Enregistrement interactif depuis la webcam")
    p_web.add_argument("--sign",    required=True, choices=CLASSES, metavar="SIGNE",
                       help="Nom du signe à enregistrer")
    p_web.add_argument("--samples", type=int, default=30,
                       help="Nombre de captures (défaut : 30)")
    p_web.add_argument("--augment", type=int, default=7,
                       help="Variantes augmentées par capture (défaut : 7 → ×8 total)")
    p_web.add_argument("--output",  default="dataset.json",
                       help="Fichier JSON de sortie (défaut : dataset.json)")
    p_web.add_argument("--append",  action="store_true",
                       help="Ajouter aux données existantes plutôt que d'écraser")

    # ── video ──
    p_vid = sub.add_parser("video", help="Extraction depuis un fichier vidéo")
    p_vid.add_argument("--sign",   required=True, choices=CLASSES, metavar="SIGNE")
    p_vid.add_argument("--input",  required=True, help="Chemin vers le fichier vidéo")
    p_vid.add_argument("--skip",   type=int, default=3,
                       help="Traiter 1 frame sur N (défaut : 3)")
    p_vid.add_argument("--augment",type=int, default=7)
    p_vid.add_argument("--output", default="dataset.json")
    p_vid.add_argument("--append", action="store_true")

    # ── images ──
    p_img = sub.add_parser("images", help="Extraction depuis un dossier d'images")
    p_img.add_argument("--sign",   required=True, choices=CLASSES, metavar="SIGNE")
    p_img.add_argument("--input",  required=True, help="Dossier contenant les images")
    p_img.add_argument("--augment",type=int, default=7)
    p_img.add_argument("--output", default="dataset.json")
    p_img.add_argument("--append", action="store_true")

    # ── stats ──
    p_sta = sub.add_parser("stats", help="Affiche les statistiques d'un dataset")
    p_sta.add_argument("file", help="Fichier JSON")

    # ── merge ──
    p_mrg = sub.add_parser("merge", help="Fusionne plusieurs fichiers JSON")
    p_mrg.add_argument("files", nargs="+", help="Fichiers JSON à fusionner")
    p_mrg.add_argument("--output", default="dataset_merged.json")

    args = parser.parse_args()

    dispatch = {
        "webcam": mode_webcam,
        "video":  mode_video,
        "images": mode_images,
        "stats":  mode_stats,
        "merge":  mode_merge,
    }
    dispatch[args.cmd](args)


if __name__ == "__main__":
    main()
