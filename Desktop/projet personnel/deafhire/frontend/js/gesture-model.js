/* =========================================================
   DeafHire — Gesture Model
   Couche de classification intermédiaire entre le modèle TF.js
   entraîné et les règles géométriques.

   Approche :
     1. Catégoriser le geste de chaque main en 7 classes standard
        (Open_Palm, Closed_Fist, Victory, Pointing_Up, Thumb_Up,
        Thumb_Down, ILoveYou) à partir des landmarks Holistic.
     2. Mapper la combinaison (gesture × contexte) vers l'un des
        14 signes LSF avec disambiguation basée sur :
          • Les deux mains ou une seule
          • La position du poignet (hauteur, côté)
          • La proximité avec des repères pose (nez, poitrine)

   Avantage : aucune requête réseau, aucun modèle supplémentaire —
   même données que SignDetector._onResults(), résultat immédiat.
   ========================================================= */

'use strict';

class GestureModel {

  /* ── Seuils ── */
  static MIN_EXT   = 1.15;   // score extension minimum pour "doigt tendu"
  static MAX_CURL  = 1.00;   // score extension maximum pour "doigt replié"
  static MIN_CONF  = 0.62;   // confiance minimum pour retourner un résultat

  /* ── Point d'entrée principal ──────────────────────────────
     Retourne { sign, confidence } ou null.
  */
  static classify(landmarks) {
    if (!landmarks) return null;
    const { rightHand: rh, leftHand: lh, pose } = landmarks;

    const rg = GestureModel._gesture(rh);
    const lg = GestureModel._gesture(lh);

    // Au moins une main doit être détectée
    if (!rg && !lg) return null;

    return GestureModel._toSign(rg, lg, rh, lh, pose);
  }

  /* ── Classification du geste d'une main ───────────────────
     Retourne { name, score } ou null.
     name ∈ { Open_Palm, Closed_Fist, Victory, Pointing_Up,
               Thumb_Up, Thumb_Down, ILoveYou }
  */
  static _gesture(hand) {
    if (!hand) return null;

    const e = {
      thumb:  GestureModel._thumbExt(hand),
      index:  GestureModel._ext(hand, 8,  6),
      middle: GestureModel._ext(hand, 12, 10),
      ring:   GestureModel._ext(hand, 16, 14),
      pinky:  GestureModel._ext(hand, 20, 18),
    };

    const T = GestureModel.MIN_EXT;
    const C = GestureModel.MAX_CURL;

    const open    = e.index > T && e.middle > T && e.ring > T && e.pinky > T;
    const victory = e.index > T && e.middle > T && e.ring < C && e.pinky < C;
    const point   = e.index > T && e.middle < C && e.ring < C && e.pinky < C;
    const iLoveU  = e.index > T && e.pinky  > T && e.middle < C && e.ring < C;
    const fisted  = e.index < C && e.middle < C && e.ring  < C && e.pinky < C;

    const thumbUp = hand[4] && hand[3] && hand[2] &&
                    hand[4].y < hand[3].y - 0.015 &&
                    hand[4].y < hand[2].y;
    const thumbDn = hand[4] && hand[3] &&
                    hand[4].y > hand[3].y + 0.015;

    // Ordered from most specific to most general
    if (iLoveU)              return { name: 'ILoveYou',    score: 0.78 };
    if (open)                return { name: 'Open_Palm',   score: Math.min(e.index, e.middle, e.ring, e.pinky) / 1.8 };
    if (victory)             return { name: 'Victory',     score: Math.min(e.index, e.middle) / 2.0 };
    if (point)               return { name: 'Pointing_Up', score: e.index / 2.0 };
    if (fisted && thumbUp)   return { name: 'Thumb_Up',    score: GestureModel._ratioConf(hand[3].y - hand[4].y, 0.015, 0.12) };
    if (fisted && thumbDn)   return { name: 'Thumb_Down',  score: 0.70 };
    if (fisted)              return { name: 'Closed_Fist', score: GestureModel._ratioConf(C - (e.index + e.middle + e.ring + e.pinky) / 4, 0, C) };

    return null;
  }

  /* ── Mapping geste(s) → signe LSF ─────────────────────────
     Priorité : main droite en premier, sauf si signe à 2 mains.
  */
  static _toSign(rg, lg, rh, lh, pose) {
    const bothHands = !!rh && !!lh;
    const g         = rg ?? lg;          // geste primaire
    const hand      = rh ?? lh;          // main primaire

    if (!g || !hand) return null;

    switch (g.name) {

      /* ── Thumb_Up → Compétence ── */
      case 'Thumb_Up':
        return { sign: 'Compétence', confidence: 0.56 + g.score * 0.32 };

      /* ── Closed_Fist → Oui  (2 mains : Travail) ── */
      case 'Closed_Fist':
        if (bothHands && lg?.name === 'Closed_Fist') {
          return { sign: 'Travail', confidence: 0.62 + Math.min(rg?.score ?? 0, lg?.score ?? 0) * 0.22 };
        }
        return { sign: 'Oui', confidence: 0.56 + g.score * 0.26 };

      /* ── Open_Palm → Bonjour / Merci / Expérience / Équipe / Futur ── */
      case 'Open_Palm': {
        // Deux mains ouvertes
        if (bothHands && lg?.name === 'Open_Palm') {
          if (rh && lh) {
            const wristDist = Math.hypot(rh[0].x - lh[0].x, rh[0].y - lh[0].y);
            if (wristDist < 0.20) return { sign: 'Équipe',     confidence: 0.63 };
            return              { sign: 'Expérience', confidence: 0.66 };
          }
        }
        // Main unique — disambiguation par position
        const wrist = hand[0];
        // Haut du cadre (front) → Bonjour
        if (wrist.y < 0.40) return { sign: 'Bonjour', confidence: 0.63 + GestureModel._ratioConf(0.40 - wrist.y, 0, 0.25) * 0.20 };
        // Droite du cadre → Futur
        if (wrist.x > 0.58) return { sign: 'Futur',   confidence: 0.60 + GestureModel._ratioConf(wrist.x - 0.58, 0, 0.25) * 0.18 };
        // Zone médiane → Merci ou Répéter
        if (wrist.y > 0.40 && wrist.y < 0.68) return { sign: 'Merci',   confidence: 0.60 };
        return { sign: 'Répéter', confidence: 0.58 };
      }

      /* ── Victory → Formation (Répéter si mouvement, non détectable ici) ── */
      case 'Victory':
        return { sign: 'Formation', confidence: 0.62 + Math.min(rg?.score ?? 0, 0.5) * 0.22 };

      /* ── Pointing_Up → Non / Je-Moi / Comprendre ── */
      case 'Pointing_Up': {
        const indexTip = hand[8];

        // Index près du visage → Comprendre
        if (pose) {
          const nose = pose[0];
          const dNose = Math.hypot(indexTip.x - nose.x, indexTip.y - nose.y);
          if (dNose < 0.16)
            return { sign: 'Comprendre', confidence: 0.60 + GestureModel._ratioConf(0.16 - dNose, 0, 0.16) * 0.28 };
        }

        // Index vers la poitrine → Je / Moi
        if (pose && pose[11] && pose[12]) {
          const chestX = (pose[11].x + pose[12].x) / 2;
          const chestY = (pose[11].y + pose[12].y) / 2;
          const dChest = Math.hypot(indexTip.x - chestX, indexTip.y - chestY);
          if (dChest < 0.16)
            return { sign: 'Je / Moi', confidence: 0.60 + GestureModel._ratioConf(0.16 - dChest, 0, 0.16) * 0.26 };
        }

        return { sign: 'Non', confidence: 0.62 + g.score * 0.18 };
      }

      /* ── ILoveYou — pas utilisé dans notre vocabulaire ── */
      case 'ILoveYou':
        return null;

      default:
        return null;
    }
  }

  /* ── Helpers ── */

  /* Extension score pouce (tip vs base MCP) */
  static _thumbExt(hand) {
    const tip   = hand[4];
    const base  = hand[2];
    const wrist = hand[0];
    if (!tip || !base || !wrist) return 0;
    const dTip  = Math.hypot(tip.x - wrist.x, tip.y - wrist.y);
    const dBase = Math.hypot(base.x - wrist.x, base.y - wrist.y);
    return dBase > 0 ? Math.min(dTip / dBase, 2) : 0;
  }

  /* Extension score générique tip vs pip */
  static _ext(hand, tipIdx, pipIdx) {
    const tip   = hand[tipIdx];
    const pip   = hand[pipIdx];
    const wrist = hand[0];
    if (!tip || !pip || !wrist) return 0;
    const dTip = Math.hypot(tip.x - wrist.x, tip.y - wrist.y, (tip.z  || 0) - (wrist.z || 0));
    const dPip = Math.hypot(pip.x - wrist.x, pip.y - wrist.y, (pip.z  || 0) - (wrist.z || 0));
    return dPip > 0 ? Math.min(dTip / dPip, 2) : 0;
  }

  static _ratioConf(value, min, max) {
    if (value <= min) return 0;
    if (value >= max) return 1;
    return (value - min) / (max - min);
  }
}

window.GestureModel = GestureModel;
