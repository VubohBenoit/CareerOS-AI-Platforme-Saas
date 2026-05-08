"""
LSF Sign Recognition Model
Architecture: LSTM over MediaPipe landmark sequences.

Input  : sequences of shape (T, 126) — 21 right-hand + 21 left-hand landmarks × 3 coords
Output : sign label probabilities

Training: see train.py
"""

import numpy as np

# Labels — must match the order used during training
SIGN_LABELS = [
    "Bonjour", "Merci", "Oui", "Non", "Je / Moi",
    "Travail", "Expérience", "Formation", "Comprendre",
    "Répéter", "Question", "Compétence", "Équipe", "Futur",
    "Neutre",
]


def extract_features(landmarks: dict) -> np.ndarray:
    """
    Extract a flat feature vector from MediaPipe holistic landmarks.
    Returns shape (126,) = 21 right-hand pts × 3 + 21 left-hand pts × 3.
    """
    def flatten(pts, n=21):
        if pts is None:
            return np.zeros(n * 3)
        arr = [[p["x"], p["y"], p["z"]] for p in pts[:n]]
        return np.array(arr).flatten()

    right = flatten(landmarks.get("rightHand"))
    left = flatten(landmarks.get("leftHand"))
    return np.concatenate([right, left])


class SignClassifier:
    """Wraps an ONNX or sklearn model for inference."""

    def __init__(self, model_path: str):
        self.model = None
        self.labels = SIGN_LABELS
        self._load(model_path)

    def _load(self, path: str):
        try:
            import onnxruntime as ort
            self.model = ort.InferenceSession(path)
            self._backend = "onnx"
        except Exception:
            try:
                import pickle
                with open(path, "rb") as f:
                    self.model = pickle.load(f)
                self._backend = "sklearn"
            except Exception:
                self.model = None
                self._backend = "none"

    def predict(self, features: np.ndarray) -> tuple[str, float]:
        """Returns (sign_label, confidence)."""
        if self.model is None:
            return "Neutre", 0.0

        if self._backend == "onnx":
            inp = {self.model.get_inputs()[0].name: features[np.newaxis].astype(np.float32)}
            probs = self.model.run(None, inp)[0][0]
        else:
            probs = self.model.predict_proba(features[np.newaxis])[0]

        idx = int(np.argmax(probs))
        return self.labels[idx], float(probs[idx])
