/* =========================================================
   DeafHire — Avatar / Text-to-Sign Display
   Converts recruiter text into visual sign cues for the
   deaf candidate: simplified text + LSF keyword chips.
   ========================================================= */

'use strict';

class SignAvatar {
  constructor(textEl, chipsEl) {
    this.textEl = textEl;       /* element showing simplified text */
    this.chipsEl = chipsEl;     /* element showing sign chips */
  }

  /* LSF keyword mapping: French word → LSF sign label */
  static LSF_KEYWORDS = {
    // Salutations
    'bonjour': 'BONJOUR', 'bonsoir': 'BONSOIR', 'salut': 'SALUT',
    'au revoir': 'AU-REVOIR', 'merci': 'MERCI', 'bienvenue': 'BIENVENUE',

    // Pronoms
    'vous': 'VOUS', 'tu': 'TU', 'je': 'JE', 'moi': 'MOI', 'nous': 'NOUS',
    'il': 'IL', 'elle': 'ELLE',

    // Verbes courants
    'parler': 'PARLER', 'expliquer': 'EXPLIQUER', 'comprendre': 'COMPRENDRE',
    'travailler': 'TRAVAILLER', 'apprendre': 'APPRENDRE', 'faire': 'FAIRE',
    'avoir': 'AVOIR', 'être': 'ÊTRE', 'vouloir': 'VOULOIR', 'pouvoir': 'POUVOIR',
    'voir': 'VOIR', 'connaître': 'CONNAÎTRE', 'savoir': 'SAVOIR',
    'aimer': 'AIMER', 'chercher': 'CHERCHER',

    // Mots de recrutement
    'expérience': 'EXPÉRIENCE', 'formation': 'FORMATION', 'compétence': 'COMPÉTENCE',
    'poste': 'POSTE', 'travail': 'TRAVAIL', 'emploi': 'EMPLOI', 'entreprise': 'ENTREPRISE',
    'équipe': 'ÉQUIPE', 'projet': 'PROJET', 'diplôme': 'DIPLÔME', 'cv': 'CV',
    'salaire': 'SALAIRE', 'entretien': 'ENTRETIEN', 'candidat': 'CANDIDAT',
    'recruteur': 'RECRUTEUR', 'manager': 'MANAGER', 'responsable': 'RESPONSABLE',
    'objectif': 'OBJECTIF', 'motivation': 'MOTIVATION', 'qualité': 'QUALITÉ',
    'défaut': 'DÉFAUT', 'force': 'FORCE', 'réussite': 'RÉUSSITE', 'défi': 'DÉFI',

    // Temps
    'maintenant': 'MAINTENANT', 'futur': 'FUTUR', 'passé': 'PASSÉ', 'avant': 'AVANT',
    'après': 'APRÈS', 'aujourd\'hui': 'AUJOURD\'HUI', 'demain': 'DEMAIN',
    'an': 'AN', 'année': 'ANNÉE', 'mois': 'MOIS',

    // Questions
    'pourquoi': 'POURQUOI', 'comment': 'COMMENT', 'quand': 'QUAND', 'où': 'OÙ',
    'quoi': 'QUOI', 'qui': 'QUI', 'quel': 'QUEL', 'quelle': 'QUELLE',
    'combien': 'COMBIEN',

    // Réponses
    'oui': 'OUI', 'non': 'NON', 'peut-être': 'PEUT-ÊTRE',
    'bien': 'BIEN', 'très': 'TRÈS', 'peu': 'PEU', 'beaucoup': 'BEAUCOUP',
  };

  /* Simplify a sentence: break long phrases, remove filler words */
  static simplify(text) {
    const fillers = ['euh', 'alors', 'donc', 'voilà', 'en fait', 'du coup', 'c\'est-à-dire'];
    let simplified = text.toLowerCase();
    fillers.forEach(f => { simplified = simplified.replaceAll(f, ''); });
    simplified = simplified
      .replace(/\s+/g, ' ')
      .trim()
      .replace(/(.{60,}?)[.!?]/, '$1.\n');
    return simplified.charAt(0).toUpperCase() + simplified.slice(1);
  }

  /* Extract LSF keywords from text */
  static extractKeywords(text) {
    const lower = text.toLowerCase();
    const found = [];

    /* Multi-word first */
    Object.keys(SignAvatar.LSF_KEYWORDS).sort((a, b) => b.length - a.length).forEach(word => {
      if (lower.includes(word) && !found.find(f => f.word === word)) {
        found.push({ word, sign: SignAvatar.LSF_KEYWORDS[word] });
      }
    });

    return found.slice(0, 8); /* max 8 chips to avoid overflow */
  }

  /* Render the sign display for a given recruiter message */
  render(text) {
    const simplified = SignAvatar.simplify(text);
    const keywords = SignAvatar.extractKeywords(text);

    /* Update simplified text */
    this.textEl.textContent = simplified || text;

    /* Render sign chips with staggered animation */
    this.chipsEl.innerHTML = '';
    if (keywords.length === 0) {
      const empty = document.createElement('span');
      empty.className = 'sign-chip-empty';
      empty.textContent = 'Aucun signe LSF identifié';
      this.chipsEl.appendChild(empty);
      return;
    }

    keywords.forEach(({ sign }, i) => {
      const chip = document.createElement('span');
      chip.className = 'sign-chip';
      chip.textContent = sign;
      chip.style.animationDelay = `${i * 60}ms`;
      chip.title = `Signe LSF : ${sign}`;
      this.chipsEl.appendChild(chip);
    });
  }

  clear() {
    this.textEl.textContent = '—';
    this.chipsEl.innerHTML = '<span class="sign-chip-empty">En attente d\'un message…</span>';
  }
}

window.SignAvatar = SignAvatar;
