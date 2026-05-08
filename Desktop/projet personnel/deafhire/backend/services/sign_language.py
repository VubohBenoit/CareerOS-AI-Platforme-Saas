"""
Sign Language Recognition Service
Translates LSF hand keypoints → French text.

Pipeline:
  Browser (MediaPipe landmarks) → WebSocket → this service → French sentence

Model loading:
  1. Tries to load the trained model from SIGN_MODEL_PATH (.pkl)
  2. Falls back to a rule-based demo classifier if no model is found

To train a real model: see ml/src/train.py or ml/src/create_demo_model.py
"""

import time
import pickle
import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class SignResult:
    sign: str
    text: str
    confidence: float
    latency_ms: int


SIGN_TO_SENTENCE: dict[str, str] = {
    "Bonjour":      "Bonjour, je suis ravi(e) de vous rencontrer.",
    "Merci":        "Merci pour cette opportunité.",
    "Oui":          "Oui, absolument.",
    "Non":          "Non, ce n'est pas le cas.",
    "Je / Moi":     "Je me présente.",
    "Travail":      "J'ai de l'expérience dans ce domaine.",
    "Expérience":   "J'ai plusieurs années d'expérience.",
    "Formation":    "J'ai suivi une formation spécialisée.",
    "Comprendre":   "J'ai bien compris votre question.",
    "Répéter":      "Pourriez-vous répéter s'il vous plaît ?",
    "Question":     "J'ai une question à vous poser.",
    "Compétence":   "C'est l'une de mes compétences clés.",
    "Équipe":       "J'apprécie le travail en équipe.",
    "Futur":        "À terme, je souhaite évoluer.",
    "Neutre":       "",
}

DEMO_SIGNS = list(SIGN_TO_SENTENCE.keys())


class SignLanguageService:

    def __init__(self):
        self._model      = None
        self._le         = None
        self._labels     = None
        self._mode       = "demo"
        self._load_model()

    def _load_model(self):
        path = Path(settings.SIGN_MODEL_PATH)
        if not path.exists():
            logger.warning(f"[SignLang] Model not found at {path} — using demo mode")
            return
        try:
            with open(path, "rb") as f:
                bundle = pickle.load(f)
            self._model  = bundle["model"]
            self._le     = bundle["label_encoder"]
            self._labels = bundle.get("labels", list(SIGN_TO_SENTENCE.keys()))
            self._mode   = "model"
            logger.info(f"[SignLang] Model loaded from {path} ({len(self._labels)} classes)")
        except Exception as exc:
            logger.error(f"[SignLang] Failed to load model: {exc} — using demo mode")

    def translate(self, payload: dict) -> SignResult:
        t0 = time.monotonic()

        # If sign label already resolved by client-side rule-based detector
        sign = payload.get("sign")
        confidence = payload.get("confidence", 0.75)

        if not sign and self._mode == "model":
            sign, confidence = self._classify_model(payload.get("keypoints", {}))
        elif not sign:
            sign = self._classify_demo()
            confidence = 0.70

        sign = sign or "Neutre"
        sentence = SIGN_TO_SENTENCE.get(sign, f"[Signe : {sign}]")
        latency = int((time.monotonic() - t0) * 1000)

        return SignResult(sign=sign, text=sentence, confidence=confidence, latency_ms=latency)

    def _classify_model(self, keypoints: dict) -> tuple[str, float]:
        """Run ML model on landmark keypoints."""
        try:
            features = self._extract_features(keypoints)
            probs = self._model.predict_proba([features])[0]
            idx   = int(np.argmax(probs))
            label = self._le.inverse_transform([idx])[0]
            return label, float(probs[idx])
        except Exception as exc:
            logger.debug(f"[SignLang] Model inference error: {exc}")
            return self._classify_demo(), 0.60

    def _classify_demo(self) -> str:
        """Round-robin demo — cycles through known signs."""
        import random
        return random.choice([s for s in DEMO_SIGNS if s != "Neutre"])

    def _extract_features(self, keypoints: dict) -> list[float]:
        """
        Flatten MediaPipe hand landmarks to a 126-dim feature vector.
        keypoints = { "rightHand": [{x,y,z}×21], "leftHand": [{x,y,z}×21] }
        """
        def flatten(pts, n=21):
            if not pts:
                return [0.0] * n * 3
            flat = []
            for p in pts[:n]:
                flat += [p.get("x", 0.0), p.get("y", 0.0), p.get("z", 0.0)]
            while len(flat) < n * 3:
                flat.append(0.0)
            return flat[:n * 3]

        right = flatten(keypoints.get("rightHand"))
        left  = flatten(keypoints.get("leftHand"))
        return right + left
