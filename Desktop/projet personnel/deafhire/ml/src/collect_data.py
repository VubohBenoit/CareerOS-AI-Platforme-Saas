"""
LSF Keypoint Data Collector
Opens the webcam and records MediaPipe landmarks for each sign.

Usage:
  pip install mediapipe opencv-python
  python collect_data.py --sign "Bonjour" --samples 200 --output data/keypoints.csv

Controls:
  SPACE  — capture one frame
  Q      — quit
"""

import argparse
import csv
import os
import time

import cv2
import mediapipe as mp

mp_holistic = mp.solutions.holistic
mp_draw = mp.solutions.drawing_utils

HEADER = ["label"] + [f"{axis}{i}" for i in range(42) for axis in ("x", "y", "z")]


def collect(sign: str, n_samples: int, output: str):
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    write_header = not os.path.exists(output)

    cap = cv2.VideoCapture(0)
    collected = 0

    with mp_holistic.Holistic(
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    ) as holistic, open(output, "a", newline="") as f:

        writer = csv.writer(f)
        if write_header:
            writer.writerow(HEADER)

        print(f"Collecting {n_samples} samples for sign: '{sign}'")
        print("Press SPACE to capture, Q to quit.")

        while collected < n_samples:
            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = holistic.process(rgb)

            def pts(landmarks, n=21):
                if landmarks is None:
                    return [0.0] * n * 3
                flat = []
                for lm in landmarks.landmark[:n]:
                    flat += [lm.x, lm.y, lm.z]
                return flat

            right = pts(results.right_hand_landmarks)
            left = pts(results.left_hand_landmarks)
            row = [sign] + right + left

            # Overlay
            cv2.putText(frame, f"Sign: {sign} | Captured: {collected}/{n_samples}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Collect LSF Data", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord(" ") and (results.right_hand_landmarks or results.left_hand_landmarks):
                writer.writerow(row)
                collected += 1
                time.sleep(0.05)
            elif key == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Done. {collected} samples saved to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sign",    required=True)
    parser.add_argument("--samples", type=int, default=200)
    parser.add_argument("--output",  default="data/keypoints.csv")
    args = parser.parse_args()
    collect(args.sign, args.samples, args.output)
