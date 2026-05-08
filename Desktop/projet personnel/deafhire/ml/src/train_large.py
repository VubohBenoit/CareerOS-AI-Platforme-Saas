#!/usr/bin/env python3
"""
DeafHire — Entraînement grand modèle LSF (500+ signes)
=======================================================
Entraîne un MLP profond sur le dataset JSON généré par spreadthesign_scraper.py
ou collect_dataset.py, puis exporte en format TF.js pour le navigateur.

Architecture : 126 → Dense(512) → BN → Drop(0.3)
                    → Dense(256) → BN → Drop(0.25)
                    → Dense(128) → Drop(0.2)
                    → Dense(N_classes, softmax)

Usage :
  python train_large.py
  python train_large.py --data ../data/dataset_sts.json --epochs 150
  python train_large.py --data ../data/dataset_sts.json --min-samples 20 --epochs 200

Sortie :
  ml/model/tfjs_model/    ← modèle TF.js (chargeable par le navigateur)
  ml/model/classes.json   ← liste des classes dans l'ordre
  ml/model/report.txt     ← rapport de précision
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT_DIR   = Path(__file__).parent.parent
DATA_DIR   = ROOT_DIR / "data"
MODEL_DIR  = ROOT_DIR / "model"
TFJS_DIR   = MODEL_DIR / "tfjs_model"
LABELS_OUT = MODEL_DIR / "classes.json"
REPORT_OUT = MODEL_DIR / "report.txt"

FEATURE_DIM = 126   # 21 landmarks × 3 coords × 2 mains


# ── Chargement du dataset ──────────────────────────────────────────────────
def load_dataset(path: Path, min_samples: int):
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    classes = sorted(k for k, v in raw.items() if len(v) >= min_samples)
    if len(classes) < 2:
        sys.exit(f"❌  Moins de 2 classes avec ≥ {min_samples} exemples. "
                 f"Lancez d'abord spreadthesign_scraper.py.")

    X, y = [], []
    for idx, cls in enumerate(classes):
        for feat in raw[cls]:
            if len(feat) == FEATURE_DIM:
                X.append(feat)
                y.append(idx)

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int32)

    print(f"  {len(classes)} classes  |  {len(X)} exemples  "
          f"| moy {len(X)//len(classes)} ex/classe")
    return X, y, classes


# ── Construction du modèle ─────────────────────────────────────────────────
def build_model(n_classes: int):
    import tensorflow as tf
    from tensorflow.keras import layers, regularizers

    reg = regularizers.l2(1e-4)

    model = tf.keras.Sequential([
        layers.Input(shape=(FEATURE_DIM,)),

        layers.Dense(512, activation="relu", kernel_regularizer=reg),
        layers.BatchNormalization(),
        layers.Dropout(0.30),

        layers.Dense(256, activation="relu", kernel_regularizer=reg),
        layers.BatchNormalization(),
        layers.Dropout(0.25),

        layers.Dense(128, activation="relu", kernel_regularizer=reg),
        layers.Dropout(0.20),

        layers.Dense(n_classes, activation="softmax"),
    ], name="lsf_mlp_large")

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


# ── Entraînement ───────────────────────────────────────────────────────────
def train(args):
    import tensorflow as tf
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report

    print(f"\n{'═'*60}")
    print(f"  DeafHire — Entraînement grand modèle LSF")
    print(f"{'═'*60}\n")

    # ── Data
    print("📂  Chargement du dataset…")
    X, y, classes = load_dataset(args.data, args.min_samples)
    n_classes = len(classes)

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.15, stratify=y, random_state=42
    )
    print(f"  Train : {len(X_train)}  |  Val : {len(X_val)}\n")

    # ── Model
    print(f"🧠  Architecture : 126 → 512 → 256 → 128 → {n_classes}")
    model = build_model(n_classes)
    model.summary(print_fn=lambda s: print("  " + s))
    print()

    # ── Callbacks
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=20,
            restore_best_weights=True, verbose=1,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5,
            patience=8, min_lr=1e-5, verbose=1,
        ),
    ]

    # ── Train
    print(f"🏋️   Entraînement ({args.epochs} epochs max)…\n")
    t0 = time.time()
    hist = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=args.epochs,
        batch_size=64,
        callbacks=callbacks,
        verbose=1,
    )
    elapsed = time.time() - t0

    # ── Évaluation
    val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
    y_pred = np.argmax(model.predict(X_val, verbose=0), axis=1)

    # Rapport par classe (top 20)
    report = classification_report(
        y_val, y_pred,
        target_names=classes,
        zero_division=0,
    )

    print(f"\n{'─'*60}")
    print(f"  Val accuracy : {val_acc*100:.1f}%")
    print(f"  Val loss     : {val_loss:.4f}")
    print(f"  Durée        : {elapsed:.0f}s")
    print(f"{'─'*60}\n")

    # ── Sauvegarde rapport
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORT_OUT, "w", encoding="utf-8") as f:
        f.write(f"DeafHire LSF Large Model — Rapport d'entraînement\n")
        f.write(f"Classes      : {n_classes}\n")
        f.write(f"Exemples     : {len(X)}\n")
        f.write(f"Val accuracy : {val_acc*100:.1f}%\n")
        f.write(f"Durée        : {elapsed:.0f}s\n\n")
        f.write(report)
    print(f"📄  Rapport → {REPORT_OUT}")

    # ── Export TF.js
    print(f"\n📦  Export TF.js → {TFJS_DIR}…")
    try:
        import tensorflowjs as tfjs
        TFJS_DIR.mkdir(parents=True, exist_ok=True)
        tfjs.converters.save_keras_model(model, str(TFJS_DIR))
        print(f"  ✅  Modèle TF.js sauvegardé")
    except ImportError:
        print("  ⚠️  tensorflowjs non installé — sauvegarde Keras uniquement")
        model.save(str(MODEL_DIR / "lsf_large.keras"))
        print(f"  Lancez : tensorflowjs_converter --input_format keras "
              f"lsf_large.keras {TFJS_DIR}")

    # ── Classes JSON
    with open(LABELS_OUT, "w", encoding="utf-8") as f:
        json.dump(classes, f, ensure_ascii=False, indent=2)
    print(f"📋  Classes → {LABELS_OUT}  ({n_classes} signes)")

    print(f"\n{'═'*60}")
    print(f"  Terminé ! Précision : {val_acc*100:.1f}%")
    print(f"\n  Étapes suivantes :")
    print(f"  1. Lancez le backend : cd backend && uvicorn main:app")
    print(f"  2. Le modèle est servi automatiquement à /model/")
    print(f"  3. Ouvrez l'entretien — la détection utilise le grand modèle")
    print(f"{'═'*60}\n")

    return val_acc


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    # Trouver automatiquement le meilleur dataset disponible
    default_data = None
    for candidate in [
        DATA_DIR / "dataset_sts.json",
        DATA_DIR / "dataset_lsf.json",
        DATA_DIR / "dataset.json",
    ]:
        if candidate.exists():
            default_data = candidate
            break

    p = argparse.ArgumentParser(
        description="DeafHire — Entraînement grand modèle LSF (TF.js export)"
    )
    p.add_argument("--data", type=Path, default=default_data,
                   help="Dataset JSON (auto-détecté si non spécifié)")
    p.add_argument("--min-samples", type=int, default=10,
                   help="Exemples minimum par classe (défaut: 10)")
    p.add_argument("--epochs", type=int, default=150,
                   help="Epochs maximum (défaut: 150, early stopping actif)")
    args = p.parse_args()

    if args.data is None or not args.data.exists():
        sys.exit(
            "❌  Aucun dataset trouvé.\n"
            "    Lancez d'abord :\n"
            "      python src/spreadthesign_scraper.py all --limit 500\n"
            "    ou :\n"
            "      python src/download_lsf_videos.py all"
        )

    train(args)


if __name__ == "__main__":
    main()
