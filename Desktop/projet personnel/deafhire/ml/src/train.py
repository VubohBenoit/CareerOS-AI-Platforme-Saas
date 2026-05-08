"""
LSF Model Training Script
Trains a Random Forest / LSTM classifier on collected LSF keypoint data.

Usage:
  python train.py --data data/keypoints.csv --output model/lsf_model.pkl

Data format (keypoints.csv):
  label, x0, y0, z0, x1, y1, z1, ... (126 landmark coordinates)
"""

import argparse
import pickle
from pathlib import Path

import numpy as np


def load_data(csv_path: str):
    import csv
    labels, features = [], []
    with open(csv_path) as f:
        reader = csv.reader(f)
        next(reader)                      # skip header
        for row in reader:
            labels.append(row[0])
            features.append([float(v) for v in row[1:]])
    return np.array(features), np.array(labels)


def train(data_path: str, output_path: str):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
    from sklearn.metrics import classification_report

    print(f"Loading data from {data_path}…")
    X, y = load_data(data_path)

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, stratify=y_enc, random_state=42
    )

    print("Training Random Forest…")
    clf = RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        pickle.dump({"model": clf, "label_encoder": le}, f)
    print(f"Model saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data",   default="data/keypoints.csv")
    parser.add_argument("--output", default="model/lsf_model.pkl")
    args = parser.parse_args()
    train(args.data, args.output)
