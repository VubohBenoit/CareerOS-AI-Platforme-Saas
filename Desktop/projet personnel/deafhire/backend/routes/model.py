"""
DeafHire — Routes de service du modèle TF.js
Sert les fichiers du grand modèle LSF entraîné en Python.
"""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

router = APIRouter(prefix="/model", tags=["model"])

MODEL_DIR = Path(__file__).parent.parent.parent / "ml" / "model"
TFJS_DIR  = MODEL_DIR / "tfjs_model"
CLASSES_FILE = MODEL_DIR / "classes.json"


@router.get("/status")
async def model_status():
    """Indique si un modèle TF.js entraîné est disponible."""
    model_json = TFJS_DIR / "model.json"
    if not model_json.exists():
        return {
            "available": False,
            "message":   "Aucun modèle entraîné. Lancez ml/src/train_large.py.",
        }

    n_classes = 0
    if CLASSES_FILE.exists():
        with open(CLASSES_FILE, encoding="utf-8") as f:
            n_classes = len(json.load(f))

    # Taille totale des fichiers du modèle
    total_bytes = sum(p.stat().st_size for p in TFJS_DIR.rglob("*") if p.is_file())

    return {
        "available":  True,
        "n_classes":  n_classes,
        "size_mb":    round(total_bytes / 1_048_576, 1),
        "model_url":  "/model/tfjs/model.json",
        "classes_url":"/model/classes",
    }


@router.get("/classes")
async def get_classes():
    """Retourne la liste ordonnée des classes du modèle."""
    if not CLASSES_FILE.exists():
        raise HTTPException(404, "classes.json introuvable — modèle non entraîné")
    with open(CLASSES_FILE, encoding="utf-8") as f:
        return JSONResponse(content=json.load(f))


@router.get("/tfjs/{filename:path}")
async def serve_tfjs_file(filename: str):
    """Sert les fichiers du modèle TF.js (model.json + shards binaires)."""
    target = (TFJS_DIR / filename).resolve()

    # Sécurité : empêcher la traversée de répertoire
    try:
        target.relative_to(TFJS_DIR.resolve())
    except ValueError:
        raise HTTPException(403, "Accès refusé")

    if not target.exists():
        raise HTTPException(404, f"Fichier introuvable : {filename}")

    media_type = "application/json" if filename.endswith(".json") else "application/octet-stream"
    return FileResponse(str(target), media_type=media_type)
