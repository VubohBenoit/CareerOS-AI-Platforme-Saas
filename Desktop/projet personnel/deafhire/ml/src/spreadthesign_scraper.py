#!/usr/bin/env python3
"""
DeafHire — Scraper Spreadthesign LSF
=====================================
Télécharge les vidéos de signes LSF depuis Spreadthesign.com,
extrait les landmarks MediaPipe, et génère un dataset JSON
importable dans le trainer navigateur.

Source : https://www.spreadthesign.com (European Sign Language Center)
         Ressource éducative publique — utilisation à des fins de recherche.

Prérequis :
  pip install -r requirements.txt
  (mediapipe, opencv-python, numpy, requests, beautifulsoup4)

Usage :
  # Étape 1 — Lister tous les signes disponibles (rapide, ~2 min)
  python spreadthesign_scraper.py list --output signs.json

  # Étape 2 — Télécharger les N signes les plus utiles
  python spreadthesign_scraper.py download --signs signs.json --limit 500

  # Étape 3 — Extraire les landmarks
  python spreadthesign_scraper.py extract --videos-dir ../data/sts_videos/

  # Tout faire d'un coup (plus lent)
  python spreadthesign_scraper.py all --limit 500

  # Stats du dataset généré
  python spreadthesign_scraper.py stats
"""

import argparse
import json
import math
import os
import re
import sys
import time
from pathlib import Path

# ── Dépendances ────────────────────────────────────────────────────────────
for mod, pkg in [("cv2","opencv-python"),("mediapipe","mediapipe"),
                 ("numpy","numpy"),("requests","requests"),
                 ("bs4","beautifulsoup4")]:
    try: __import__(mod)
    except ImportError: sys.exit(f"❌  Manquant : pip install {pkg}")

import cv2
import mediapipe as mp
import numpy as np
import requests
from bs4 import BeautifulSoup

# ── Config ─────────────────────────────────────────────────────────────────
BASE_URL    = "https://www.spreadthesign.com"
LANG        = "fr.fr"          # Français → LSF
DELAY_SEC   = 0.8              # Délai entre requêtes (respecter le serveur)
ROOT_DIR    = Path(__file__).parent.parent
VIDEOS_DIR  = ROOT_DIR / "data" / "sts_videos"
SIGNS_FILE  = ROOT_DIR / "data" / "sts_signs.json"
DATASET_OUT = ROOT_DIR / "data" / "dataset_sts.json"
MIN_SAMPLES = 10

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent":       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Accept":           "text/html, */*; q=0.01",
    "Referer":          f"{BASE_URL}/{LANG}/search/by-category/",
})


# ── Normalisation landmarks (identique à SignTrainer.extract JS) ───────────
def norm_hand(lm):
    if lm is None: return [0.0] * 63
    pts = [(p.x, p.y, p.z) for p in lm.landmark]
    wx, wy, wz = pts[0]
    rx, ry, rz = pts[9]
    sc = math.sqrt((rx-wx)**2+(ry-wy)**2+(rz-wz)**2) or 1e-6
    out = []
    for x, y, z in pts:
        out += [(x-wx)/sc, (y-wy)/sc, (z-wz)/sc]
    return out

def extract_features(res):
    return norm_hand(res.right_hand_landmarks) + norm_hand(res.left_hand_landmarks)

def has_hand(res):
    return res.right_hand_landmarks or res.left_hand_landmarks

def augment(feat, n=5):
    arr = np.array(feat, dtype=np.float32)
    out = [feat]
    for _ in range(n):
        out.append((arr * np.random.uniform(0.9,1.1) + np.random.normal(0,0.02,arr.shape)).tolist())
    return out


# ── HTTP helpers ───────────────────────────────────────────────────────────
def get(url, retries=3):
    for attempt in range(retries):
        try:
            r = SESSION.get(url, timeout=15)
            r.raise_for_status()
            return r
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise
    return None


# ── Étape 1 : lister tous les signes ──────────────────────────────────────
def get_categories():
    """Retourne liste de {id, slug, name} pour toutes les catégories."""
    r = get(f"{BASE_URL}/{LANG}/search/by-category/")
    cats = re.findall(
        r'href="/' + LANG + r'/search/by-category/(\d+)/([^/"]+)/"',
        r.text
    )
    # Exclure la catégorie racine
    return [{"id": cid, "slug": slug, "name": slug.replace("-", " ")}
            for cid, slug in cats if cid not in ("", "0")]


def get_words_in_category(cat_id, cat_slug):
    """Retourne liste de {id, slug, word} pour une catégorie."""
    url = f"{BASE_URL}/{LANG}/search/by-category/{cat_id}/{cat_slug}/"
    try:
        r = get(url)
        matches = re.findall(
            r'href="/' + LANG + r'/word/(\d+)/([^/"]+)/0/',
            r.text
        )
        return [{"id": wid, "slug": wslug, "word": wslug.replace("-", " ")}
                for wid, wslug in matches]
    except Exception as e:
        print(f"    ⚠  Catégorie {cat_id} inaccessible : {e}")
        return []


def get_video_url(word_id, word_slug):
    """Retourne l'URL MP4 du signe ou None."""
    url = f"{BASE_URL}/{LANG}/word/{word_id}/{word_slug}/0/"
    try:
        r = get(url)
        vids = re.findall(
            r'(https://media\.spreadthesign\.com/video/mp4/[^\s"\'<>]+\.mp4)',
            r.text
        )
        return vids[0] if vids else None
    except Exception:
        return None


def cmd_list(args):
    """Liste tous les signes disponibles et sauvegarde dans un JSON."""
    print("\n📋  Listing des signes Spreadthesign LSF…\n")
    categories = get_categories()
    print(f"  {len(categories)} catégories trouvées\n")

    all_signs = {}   # word_id → {word, slug, categories, video_url}
    total_cats = len(categories)

    for i, cat in enumerate(categories):
        print(f"\r  [{i+1}/{total_cats}] {cat['name']:<40}", end="", flush=True)
        words = get_words_in_category(cat["id"], cat["slug"])
        for w in words:
            wid = w["id"]
            if wid not in all_signs:
                all_signs[wid] = {
                    "id":         wid,
                    "word":       w["word"],
                    "slug":       w["slug"],
                    "categories": [],
                    "video_url":  None,
                }
            if cat["name"] not in all_signs[wid]["categories"]:
                all_signs[wid]["categories"].append(cat["name"])
        time.sleep(DELAY_SEC)

    signs_list = sorted(all_signs.values(), key=lambda x: x["word"])
    print(f"\n\n  ✅  {len(signs_list)} signes uniques trouvés")

    # Récupère les URLs vidéo (par lots de 5 pour aller vite)
    if args.fetch_urls:
        print(f"\n  🔗  Récupération des URLs vidéo…")
        for j, sign in enumerate(signs_list):
            if j % 50 == 0:
                print(f"\r  {j}/{len(signs_list)} URLs récupérées", end="", flush=True)
            sign["video_url"] = get_video_url(sign["id"], sign["slug"])
            time.sleep(DELAY_SEC * 0.5)
        print(f"\n  {sum(1 for s in signs_list if s['video_url'])} signes avec vidéo")

    # Sauvegarde
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(signs_list, f, ensure_ascii=False, indent=2)
    print(f"\n  💾  Sauvegardé → {args.output}\n")
    return signs_list


# ── Étape 2 : télécharger les vidéos ──────────────────────────────────────
def cmd_download(args):
    """Télécharge les vidéos MP4 pour les N premiers signes."""
    print(f"\n⬇️   Téléchargement des vidéos (limite : {args.limit} signes)\n")

    with open(args.signs, encoding="utf-8") as f:
        signs = json.load(f)

    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    downloaded = 0
    skipped    = 0
    failed     = 0

    for sign in signs[:args.limit]:
        safe = re.sub(r'[^\w\-]', '_', sign['word'])[:60]
        out  = VIDEOS_DIR / f"{sign['id']}_{safe}.mp4"

        if out.exists():
            skipped += 1
            continue

        # Récupère l'URL si pas encore dans le JSON
        video_url = sign.get("video_url")
        if not video_url:
            video_url = get_video_url(sign["id"], sign["slug"])
            time.sleep(DELAY_SEC * 0.3)

        if not video_url:
            failed += 1
            continue

        try:
            r = SESSION.get(video_url, timeout=20, stream=True)
            r.raise_for_status()
            with open(out, "wb") as f:
                for chunk in r.iter_content(65536):
                    f.write(chunk)
            downloaded += 1
            pct = int(downloaded / max(args.limit - skipped, 1) * 100)
            print(f"\r  ✓ {downloaded} téléchargés  ⊘ {skipped} existants  ✗ {failed} échecs   {sign['word'][:30]:<30}", end="", flush=True)
            time.sleep(DELAY_SEC)
        except Exception as e:
            failed += 1

    print(f"\n\n  ✅  {downloaded} nouvelles vidéos téléchargées")
    print(f"      {skipped} déjà existantes, {failed} échecs")
    print(f"      Dossier : {VIDEOS_DIR}\n")


# ── Étape 3 : extraire les landmarks ──────────────────────────────────────
def cmd_extract(args):
    """Extrait les landmarks MediaPipe de toutes les vidéos téléchargées."""
    videos_dir = args.videos_dir
    exts = {".mp4", ".avi", ".mov", ".webm"}

    files = sorted(f for f in Path(videos_dir).iterdir() if f.suffix.lower() in exts)
    if not files:
        sys.exit(f"❌  Aucune vidéo trouvée dans {videos_dir}")

    print(f"\n🧠  Extraction MediaPipe — {len(files)} vidéos\n")

    holistic = mp.solutions.holistic.Holistic(
        static_image_mode=False, model_complexity=1,
        min_detection_confidence=0.5, min_tracking_confidence=0.5,
    )

    dataset = {}
    ok = 0
    skip = 0

    for idx, vp in enumerate(files):
        # Extraire le mot depuis le nom de fichier: {id}_{word}.mp4
        parts  = vp.stem.split("_", 1)
        label  = parts[1].replace("_", " ") if len(parts) == 2 else vp.stem

        cap    = cv2.VideoCapture(str(vp))
        total  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        frames = []
        fi     = 0

        while True:
            ret, frame = cap.read()
            if not ret: break
            fi += 1
            if fi % args.skip != 0: continue
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = holistic.process(rgb)
            if has_hand(res):
                frames.append(extract_features(res))

        cap.release()

        if not frames:
            skip += 1
            print(f"\r  [{idx+1}/{len(files)}] ✗ {label[:35]:<35} (pas de main)", end="", flush=True)
            continue

        samples = []
        for feat in frames:
            samples.extend(augment(feat, args.augment))

        dataset[label] = samples
        ok += 1
        print(f"\r  [{idx+1}/{len(files)}] ✓ {label[:35]:<35} {len(samples):>5} exemples", end="", flush=True)

    holistic.close()
    print(f"\n\n  ✅  {ok} signes extraits  ✗ {skip} sans main")

    DATASET_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(DATASET_OUT, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False)

    total_samples = sum(len(v) for v in dataset.values())
    print(f"  💾  Dataset → {DATASET_OUT}  ({total_samples} exemples, {len(dataset)} signes)\n")
    cmd_stats(args)


# ── Stats ──────────────────────────────────────────────────────────────────
def cmd_stats(args):
    if not DATASET_OUT.exists():
        print(f"Aucun dataset à : {DATASET_OUT}")
        return
    with open(DATASET_OUT, encoding="utf-8") as f:
        data = json.load(f)
    total = sum(len(v) for v in data.values())
    ok    = sum(1 for v in data.values() if len(v) >= MIN_SAMPLES)
    print(f"\n📊  Dataset : {DATASET_OUT}")
    print(f"    {len(data)} signes  |  {total} exemples  |  {ok} prêts (≥{MIN_SAMPLES})")
    # Top 10
    top = sorted(data.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    print(f"\n  Top 10 :")
    for label, samples in top:
        bar = "█" * min(len(samples)//50, 20)
        print(f"    {label:<30} {len(samples):>6}  {bar}")
    print(f"\n  → Importez {DATASET_OUT.name} dans le trainer navigateur")
    print(f"    (bouton IA → Importer dans la page d'entretien)\n")


# ── All-in-one ─────────────────────────────────────────────────────────────
def cmd_all(args):
    """Liste + télécharge + extrait en une seule commande."""
    # List
    list_args = argparse.Namespace(
        output=SIGNS_FILE, fetch_urls=True,
    )
    signs = cmd_list(list_args)

    # Download
    dl_args = argparse.Namespace(
        signs=SIGNS_FILE, limit=args.limit,
    )
    cmd_download(dl_args)

    # Extract
    ext_args = argparse.Namespace(
        videos_dir=VIDEOS_DIR, skip=args.skip, augment=args.augment,
    )
    cmd_extract(ext_args)


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(
        description="DeafHire — Scraper Spreadthesign LSF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # list
    pl = sub.add_parser("list", help="Lister tous les signes disponibles")
    pl.add_argument("--output", type=Path, default=SIGNS_FILE,
                    help=f"Fichier JSON de sortie (défaut: {SIGNS_FILE})")
    pl.add_argument("--fetch-urls", action="store_true",
                    help="Récupérer aussi les URLs vidéo (plus lent)")

    # download
    pd = sub.add_parser("download", help="Télécharger les vidéos MP4")
    pd.add_argument("--signs", type=Path, default=SIGNS_FILE,
                    help="Fichier JSON de la liste des signes")
    pd.add_argument("--limit", type=int, default=500,
                    help="Nombre max de signes à télécharger (défaut: 500)")

    # extract
    pe = sub.add_parser("extract", help="Extraire les landmarks MediaPipe")
    pe.add_argument("--videos-dir", type=Path, default=VIDEOS_DIR,
                    help=f"Dossier des vidéos (défaut: {VIDEOS_DIR})")
    pe.add_argument("--skip",    type=int, default=3,
                    help="Traiter 1 frame sur N (défaut: 3)")
    pe.add_argument("--augment", type=int, default=5,
                    help="Variantes augmentées par frame (défaut: 5)")

    # all
    pa = sub.add_parser("all", help="Liste + télécharge + extrait")
    pa.add_argument("--limit",   type=int, default=500)
    pa.add_argument("--skip",    type=int, default=3)
    pa.add_argument("--augment", type=int, default=5)

    # stats
    sub.add_parser("stats", help="Statistiques du dataset généré")

    args = p.parse_args()

    dispatch = {
        "list":     cmd_list,
        "download": cmd_download,
        "extract":  cmd_extract,
        "all":      cmd_all,
        "stats":    cmd_stats,
    }
    dispatch[args.cmd](args)


if __name__ == "__main__":
    main()
