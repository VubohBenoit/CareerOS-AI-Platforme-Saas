"""
Demo Model Generator — DeafHire
Generates a functional (though not accurate on real data) sklearn model
from synthetic landmark data so the full pipeline is end-to-end runnable.

Run once before starting the backend:
    cd ml && python src/create_demo_model.py

The model will be saved to ml/model/lsf_model.pkl
Replace it with a model trained on real LSF data for production use.
"""

import pickle
import numpy as np
from pathlib import Path

SIGN_LABELS = [
    "Bonjour", "Merci", "Oui", "Non", "Je / Moi",
    "Travail", "Expérience", "Formation", "Comprendre",
    "Répéter", "Question", "Compétence", "Équipe", "Futur", "Neutre",
]

N_FEATURES = 126   # 21 right-hand + 21 left-hand landmarks × 3 coords
N_PER_CLASS = 300  # synthetic samples per sign


def _make_synthetic_data():
    """
    Generate synthetic landmark vectors per sign.
    Each sign has a characteristic "seed" pattern plus Gaussian noise.
    This allows the model to learn separable classes — accuracy on real
    hands will be low until replaced with real training data.
    """
    rng = np.random.default_rng(42)
    X, y = [], []

    for i, label in enumerate(SIGN_LABELS):
        # Unique centroid per sign — deterministic from index
        centroid = rng.uniform(0.1, 0.9, N_FEATURES)
        centroid[i * 3 % N_FEATURES] += 0.3          # discriminative feature
        centroid[(i * 7 + 1) % N_FEATURES] -= 0.2

        # Samples = centroid + small noise
        samples = centroid + rng.normal(0, 0.05, (N_PER_CLASS, N_FEATURES))
        samples = np.clip(samples, 0.0, 1.0)
        X.append(samples)
        y.extend([label] * N_PER_CLASS)

    return np.vstack(X), np.array(y)


def train_and_save(output_path: str = "model/lsf_model.pkl"):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score

    print("Generating synthetic training data…")
    X, y = _make_synthetic_data()

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.15, stratify=y_enc, random_state=42
    )

    print(f"Training RandomForest on {len(X_train)} samples, {N_FEATURES} features…")
    clf = RandomForestClassifier(n_estimators=150, max_depth=12, n_jobs=-1, random_state=42)
    clf.fit(X_train, y_train)

    acc = accuracy_score(y_test, clf.predict(X_test))
    print(f"Validation accuracy (synthetic): {acc:.1%}")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        pickle.dump({"model": clf, "label_encoder": le, "labels": SIGN_LABELS}, f)

    print(f"Model saved → {output_path}")
    print("NOTE: Replace this model with one trained on real LSF data for production use.")


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "model/lsf_model.pkl"
    train_and_save(out)
