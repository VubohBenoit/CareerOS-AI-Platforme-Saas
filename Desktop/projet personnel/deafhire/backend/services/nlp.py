"""
NLP Service
Simplifies recruiter text for better comprehension by deaf candidates,
and extracts LSF sign keywords.
"""

import re
from dataclasses import dataclass, field

# Words to remove (French fillers)
FILLER_WORDS = {
    "euh", "alors", "donc", "voilà", "hein", "quoi", "ben", "beh",
    "en fait", "du coup", "c'est-à-dire", "au fait",
}

# LSF keyword mapping (French word → LSF sign label)
LSF_KEYWORDS: dict[str, str] = {
    "bonjour": "BONJOUR", "bonsoir": "BONSOIR", "salut": "SALUT",
    "merci": "MERCI", "au revoir": "AU-REVOIR",
    "vous": "VOUS", "tu": "TU", "je": "JE", "moi": "MOI", "nous": "NOUS",
    "parler": "PARLER", "expliquer": "EXPLIQUER", "comprendre": "COMPRENDRE",
    "travailler": "TRAVAILLER", "apprendre": "APPRENDRE",
    "expérience": "EXPÉRIENCE", "formation": "FORMATION",
    "compétence": "COMPÉTENCE", "poste": "POSTE", "travail": "TRAVAIL",
    "emploi": "EMPLOI", "entreprise": "ENTREPRISE", "équipe": "ÉQUIPE",
    "projet": "PROJET", "diplôme": "DIPLÔME", "salaire": "SALAIRE",
    "objectif": "OBJECTIF", "motivation": "MOTIVATION",
    "oui": "OUI", "non": "NON",
    "pourquoi": "POURQUOI", "comment": "COMMENT", "quand": "QUAND",
    "où": "OÙ", "qui": "QUI", "quoi": "QUOI", "combien": "COMBIEN",
    "futur": "FUTUR", "passé": "PASSÉ", "aujourd'hui": "AUJOURD'HUI",
    "bien": "BIEN", "très": "TRÈS", "beaucoup": "BEAUCOUP",
}


@dataclass
class NLPResult:
    original: str
    simplified: str
    sign_keywords: list[str] = field(default_factory=list)


class NLPService:

    def process_recruiter_message(self, text: str) -> NLPResult:
        simplified = self._simplify(text)
        keywords = self._extract_keywords(text)
        return NLPResult(original=text, simplified=simplified, sign_keywords=keywords)

    def _simplify(self, text: str) -> str:
        lower = text.lower()
        for filler in FILLER_WORDS:
            lower = lower.replace(filler, "")
        lower = re.sub(r"\s+", " ", lower).strip()
        # Split overly long sentences at punctuation
        if len(lower) > 80:
            lower = re.sub(r"(?<=[.!?])\s+", "\n", lower)
        return lower.capitalize()

    def _extract_keywords(self, text: str) -> list[str]:
        lower = text.lower()
        found: list[str] = []
        # Match multi-word first, then single
        for word in sorted(LSF_KEYWORDS, key=len, reverse=True):
            if word in lower and LSF_KEYWORDS[word] not in found:
                found.append(LSF_KEYWORDS[word])
            if len(found) >= 8:
                break
        return found
