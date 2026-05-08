#!/usr/bin/env python3
"""
DeafHire — Enregistrement de TOUS les signes en séquence
=========================================================
Lance le collecteur webcam pour chaque signe, l'un après l'autre.
À la fin, génère dataset.json importable dans le trainer navigateur.

Usage :
  python record_all_signs.py
  python record_all_signs.py --samples 20 --output ../data/dataset.json
"""

import argparse
import subprocess
import sys
from pathlib import Path

CLASSES = [
    "Bonjour", "Merci", "Oui", "Non", "Je / Moi",
    "Travail", "Expérience", "Formation", "Comprendre",
    "Répéter", "Question", "Compétence", "Équipe", "Futur",
]

DESCRIPTIONS = {
    "Bonjour":    "Main ouverte, paume vers vous, au niveau du front.",
    "Merci":      "Main plate, paume vers le bas, partez du menton vers l'avant.",
    "Oui":        "Poing fermé, hochement haut ↔ bas.",
    "Non":        "Index tendu, agitation gauche ↔ droite.",
    "Je / Moi":   "Index pointé vers votre poitrine.",
    "Travail":    "Les deux poings fermés, tapez-les l'un contre l'autre.",
    "Expérience": "Les deux mains grandes ouvertes, doigts écartés.",
    "Formation":  "Signe V : index et majeur tendus.",
    "Comprendre": "Index tendu, touchez légèrement votre tempe.",
    "Répéter":    "Main semi-ouverte, mouvement circulaire.",
    "Question":   "Index courbé en crochet (forme de ? inversé).",
    "Compétence": "Pouce levé, les quatre autres doigts repliés.",
    "Équipe":     "Les deux poignets rapprochés devant vous.",
    "Futur":      "Main ouverte, poussez vers l'avant et vers la droite.",
}


def main():
    parser = argparse.ArgumentParser(description="Enregistrement de tous les signes LSF")
    parser.add_argument("--samples", type=int, default=25,
                        help="Captures par signe (défaut : 25 → ~200 exemples avec aug)")
    parser.add_argument("--augment", type=int, default=7,
                        help="Facteur d'augmentation (défaut : 7)")
    parser.add_argument("--output",  default="../data/dataset.json",
                        help="Fichier de sortie (défaut : ../data/dataset.json)")
    parser.add_argument("--start",   type=int, default=0,
                        help="Reprendre à partir du signe N (0 = début)")
    args = parser.parse_args()

    collector = Path(__file__).parent / "collect_dataset.py"
    total     = len(CLASSES)

    print("\n" + "═" * 60)
    print("  DeafHire — Collecte de données LSF")
    print(f"  {total} signes × {args.samples} captures × ×{args.augment + 1} aug")
    print(f"  → ~{total * args.samples * (args.augment + 1)} exemples au total")
    print("═" * 60)

    for i, sign in enumerate(CLASSES):
        if i < args.start:
            continue

        print(f"\n[{i + 1}/{total}] ━━━  {sign}  ━━━")
        print(f"  Comment faire : {DESCRIPTIONS.get(sign, '')}")
        print()
        input("  Appuyez sur ENTRÉE pour ouvrir la caméra…")

        cmd = [
            sys.executable, str(collector),
            "webcam",
            "--sign",    sign,
            "--samples", str(args.samples),
            "--augment", str(args.augment),
            "--output",  args.output,
            "--append",
        ]

        ret = subprocess.run(cmd)
        if ret.returncode != 0:
            print(f"\n⚠️  Erreur sur '{sign}' (code {ret.returncode})")
            rep = input("  Continuer avec le signe suivant ? [o/N] ").strip().lower()
            if rep not in ("o", "oui", "y", "yes"):
                break

    print("\n" + "═" * 60)
    print("  Collecte terminée !")
    print(f"  Fichier : {args.output}")
    print()
    print("  → Importez ce fichier dans le trainer navigateur")
    print("    (bouton 'Importer' dans le modal IA de l'entretien)")
    print("═" * 60 + "\n")

    # Affiche les stats finales
    subprocess.run([sys.executable, str(collector), "stats", args.output])


if __name__ == "__main__":
    main()
