"""
Sign Language Recognition Service
Translates ASL/LSF sign labels → French sentences.

Pipeline:
  Browser (MediaPipe landmarks + detected sign) → WebSocket → this service → French sentence

Supports both:
  - LSF sign names (French, 14 signs from the browser trainer)
  - WLASL gloss names (English ASL, from the large Python-trained model)
"""

import time
import logging
from dataclasses import dataclass

from core.config import get_settings

logger   = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class SignResult:
    sign:        str
    text:        str
    confidence:  float
    latency_ms:  int


# ── ASL gloss → French label (localization) ───────────────────────────────
ASL_TO_FRENCH: dict[str, str] = {
    # Greetings
    "hello": "Bonjour", "hi": "Bonjour",
    "goodbye": "Au revoir", "bye": "Au revoir",
    "thank you": "Merci", "thanks": "Merci",
    "please": "S'il vous plaît", "sorry": "Désolé",
    "excuse me": "Excusez-moi", "welcome": "Bienvenue",
    "you're welcome": "De rien",
    # Answers
    "yes": "Oui", "no": "Non", "maybe": "Peut-être",
    "ok": "D'accord", "fine": "Bien", "sure": "Bien sûr",
    "right": "Juste", "wrong": "Faux",
    # Pronouns
    "i": "Je / Moi", "me": "Je / Moi", "myself": "Moi-même",
    "you": "Tu / Vous", "he": "Il", "she": "Elle",
    "we": "Nous", "they": "Ils / Elles",
    # Questions
    "what": "Quoi", "where": "Où", "when": "Quand",
    "who": "Qui", "why": "Pourquoi", "how": "Comment",
    "question": "Question", "ask": "Demander",
    # Numbers
    "one": "Un", "two": "Deux", "three": "Trois",
    "four": "Quatre", "five": "Cinq", "six": "Six",
    "seven": "Sept", "eight": "Huit", "nine": "Neuf",
    "ten": "Dix", "zero": "Zéro", "number": "Nombre",
    # Professional
    "work": "Travail", "job": "Emploi",
    "experience": "Expérience", "skill": "Compétence",
    "ability": "Capacité", "study": "Formation",
    "learn": "Apprendre", "education": "Formation",
    "school": "École", "college": "Université",
    "understand": "Comprendre", "again": "Répéter",
    "repeat": "Répéter", "team": "Équipe",
    "group": "Groupe", "future": "Futur",
    "will": "Futur", "plan": "Projet",
    "goal": "Objectif", "project": "Projet",
    "meeting": "Réunion", "interview": "Entretien",
    "company": "Entreprise", "office": "Bureau",
    "manager": "Responsable", "employee": "Employé",
    "salary": "Salaire", "hire": "Embaucher",
    "teacher": "Professeur", "student": "Étudiant",
    "together": "Ensemble",
    # Common verbs
    "go": "Aller", "come": "Venir", "help": "Aide",
    "want": "Vouloir", "need": "Besoin", "like": "Apprécier",
    "love": "Aimer", "think": "Penser", "know": "Savoir",
    "see": "Voir", "look": "Regarder", "listen": "Écouter",
    "talk": "Parler", "speak": "Parler", "say": "Dire",
    "make": "Faire", "do": "Faire", "finish": "Terminé",
    "start": "Commencer", "stop": "Arrêter", "wait": "Attendre",
    "give": "Donner", "take": "Prendre", "find": "Trouver",
    "write": "Écrire", "read": "Lire", "open": "Ouvrir",
    "close": "Fermer", "play": "Jouer", "eat": "Manger",
    "drink": "Boire", "sleep": "Dormir",
    # Adjectives
    "good": "Bon", "bad": "Mauvais", "great": "Excellent",
    "happy": "Heureux", "sad": "Triste", "tired": "Fatigué",
    "sick": "Malade", "hot": "Chaud", "cold": "Froid",
    "big": "Grand", "small": "Petit", "new": "Nouveau",
    "old": "Ancien", "fast": "Rapide", "slow": "Lent",
    "hard": "Difficile", "easy": "Facile", "clean": "Propre",
    # Time
    "now": "Maintenant", "today": "Aujourd'hui",
    "tomorrow": "Demain", "yesterday": "Hier",
    "morning": "Matin", "night": "Nuit", "time": "Temps",
    "before": "Avant", "after": "Après", "later": "Plus tard",
    # Family
    "family": "Famille", "mother": "Mère", "father": "Père",
    "brother": "Frère", "sister": "Sœur", "friend": "Ami",
    # Places
    "home": "Maison", "school-place": "École",
    "hospital": "Hôpital", "city": "Ville",
    # Misc
    "name": "Nom", "money": "Argent", "book": "Livre",
    "water": "Eau", "food": "Nourriture",
    "deaf": "Sourd", "sign language": "Langue des signes",
    "not": "Non / Pas", "nothing": "Rien",
    "many": "Beaucoup", "all": "Tout", "some": "Quelques",
}

# ── Phrases contextuelles pour les signes connus ──────────────────────────
SIGN_TO_SENTENCE: dict[str, str] = {
    # LSF French names
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
    # Generic fallback sentences for translated ASL signs
    "Au revoir":    "Au revoir et merci pour cet entretien.",
    "D'accord":     "D'accord, je comprends.",
    "S'il vous plaît": "S'il vous plaît, pourriez-vous m'aider ?",
    "Désolé":       "Je suis désolé(e), je n'ai pas compris.",
    "Aide":         "J'aurais besoin d'aide.",
    "Vouloir":      "Je voudrais en savoir plus.",
    "Besoin":       "J'ai besoin de précisions.",
    "Apprécier":    "J'apprécie cette question.",
    "Aimer":        "J'aime beaucoup ce domaine.",
    "Penser":       "Je pense que c'est une bonne approche.",
    "Savoir":       "Je sais comment gérer cette situation.",
    "Terminé":      "J'ai terminé ma présentation.",
    "Commencer":    "Je vais commencer par vous expliquer mon parcours.",
    "Excellent":    "C'est excellent, merci.",
    "Heureux":      "Je suis heureux(se) d'être ici.",
    "Projet":       "J'ai travaillé sur plusieurs projets importants.",
    "Ensemble":     "J'aime travailler en équipe.",
    "Responsable":  "J'ai été responsable d'une équipe.",
    "Entreprise":   "J'ai travaillé dans plusieurs entreprises.",
}


def asl_to_french(gloss: str) -> str:
    """Traduit un gloss ASL (anglais) en label français."""
    return ASL_TO_FRENCH.get(gloss.lower().strip(), gloss)


def sign_to_sentence(french_label: str) -> str:
    """Retourne une phrase contextuelle pour un signe français."""
    if french_label in SIGN_TO_SENTENCE:
        return SIGN_TO_SENTENCE[french_label]
    return f"Je souhaite exprimer : {french_label}."


class SignLanguageService:

    def __init__(self):
        self._mode = "rule"
        logger.info("[SignLang] Service initialisé (mode règles + traduction ASL→FR)")

    def translate(self, payload: dict) -> SignResult:
        t0         = time.monotonic()
        sign       = payload.get("sign") or ""
        confidence = float(payload.get("confidence", 0.75))

        french_label = asl_to_french(sign) if sign else "Neutre"
        sentence     = sign_to_sentence(french_label)
        latency      = int((time.monotonic() - t0) * 1000)

        return SignResult(
            sign=french_label,
            text=sentence,
            confidence=confidence,
            latency_ms=latency,
        )
