/* =========================================================
   DeafHire — Sign Language Detector
   Uses MediaPipe Holistic to detect hand landmarks and maps
   them to a dictionary of LSF (French Sign Language) signs.
   ========================================================= */

'use strict';

class SignDetector {
  constructor(videoEl, canvasEl, onSign) {
    this.video    = videoEl;
    this.canvas   = canvasEl;
    this.ctx      = canvasEl.getContext('2d');
    this.onSign   = onSign;         /* callback(sign, confidence, landmarks) */
    this.onFrame  = null;           /* raw-frame hook for data collection */
    this.active   = false;
    this.holistic = null;
    this.camera   = null;
    this.lastSign = null;
    this.signBuffer    = [];        /* rolling buffer for stability */
    this.BUFFER_SIZE   = 8;
    this.MIN_CONFIDENCE = 0.55;
  }

  /* ── LSF sign dictionary (demo rules based on hand geometry) ──
     Each entry: { name, check: (landmarks) => confidence 0-1 }
     landmarks = { leftHand, rightHand, pose }  (MediaPipe NormalizedLandmarks)
  */
  static SIGNS = [
    {
      name: 'Bonjour',
      /* Open palm raised above mid-face */
      check({ rightHand }) {
        if (!rightHand) return 0;
        const wrist  = rightHand[0];
        const eIndex = SignDetector._extensionScore(rightHand, 8,  6);
        const eMiddle= SignDetector._extensionScore(rightHand, 12, 10);
        const eRing  = SignDetector._extensionScore(rightHand, 16, 14);
        const ePinky = SignDetector._extensionScore(rightHand, 20, 18);
        const openScore = Math.min(eIndex, eMiddle, eRing, ePinky);
        const heightConf = SignDetector._ratioConf(0.45 - wrist.y, 0, 0.2);
        return openScore >= 1.15 ? 0.6 + heightConf * 0.35 : 0;
      },
    },
    {
      name: 'Merci',
      /* Flat hand at chin level */
      check({ rightHand }) {
        if (!rightHand) return 0;
        const wrist = rightHand[0];
        const eIndex = SignDetector._extensionScore(rightHand, 8, 6);
        const eMiddle= SignDetector._extensionScore(rightHand, 12, 10);
        const openScore = Math.min(eIndex, eMiddle);
        const inZone = wrist.y > 0.42 && wrist.y < 0.68;
        const zoneConf = inZone ? SignDetector._ratioConf(0.28 - Math.abs(wrist.y - 0.55), 0, 0.28) : 0;
        return openScore >= 1.15 && inZone ? 0.58 + zoneConf * 0.32 : 0;
      },
    },
    {
      name: 'Oui',
      /* Closed fist (all fingers curled) */
      check({ rightHand }) {
        if (!rightHand) return 0;
        const scores = [8,12,16,20].map(i => {
          const pip = { 8:6, 12:10, 16:14, 20:18 }[i];
          return SignDetector._extensionScore(rightHand, i, pip);
        });
        const curl = scores.reduce((a, b) => a + b, 0) / scores.length;
        return curl < 0.95 ? SignDetector._ratioConf(0.95 - curl, 0, 0.5) * 0.85 : 0;
      },
    },
    {
      name: 'Non',
      /* Only index extended, others curled */
      check({ rightHand }) {
        if (!rightHand) return 0;
        const indexScore  = SignDetector._extensionScore(rightHand, 8, 6);
        const middleScore = SignDetector._extensionScore(rightHand, 12, 10);
        const ringScore   = SignDetector._extensionScore(rightHand, 16, 14);
        if (indexScore < 1.2 || middleScore > 1.05 || ringScore > 1.05) return 0;
        const contrast = indexScore - Math.max(middleScore, ringScore);
        return SignDetector._ratioConf(contrast, 0.1, 0.6) * 0.85;
      },
    },
    {
      name: 'Je / Moi',
      /* Index pointing toward chest */
      check({ rightHand, pose }) {
        if (!rightHand || !pose) return 0;
        const indexTip = rightHand[8];
        const chestY   = (pose[11].y + pose[12].y) / 2;
        const chestX   = (pose[11].x + pose[12].x) / 2;
        const indexScore  = SignDetector._extensionScore(rightHand, 8, 6);
        const middleScore = SignDetector._extensionScore(rightHand, 12, 10);
        if (indexScore < 1.2 || middleScore > 1.1) return 0;
        const dist = Math.hypot(indexTip.x - chestX, indexTip.y - chestY);
        return SignDetector._ratioConf(0.12 - dist, 0, 0.12) * 0.82;
      },
    },
    {
      name: 'Travail',
      /* Both hands fisted */
      check({ leftHand, rightHand }) {
        if (!leftHand || !rightHand) return 0;
        const lCurl = [8,12,16,20].map(i => SignDetector._extensionScore(leftHand,  i, {8:6,12:10,16:14,20:18}[i]));
        const rCurl = [8,12,16,20].map(i => SignDetector._extensionScore(rightHand, i, {8:6,12:10,16:14,20:18}[i]));
        const avg = [...lCurl, ...rCurl].reduce((a, b) => a + b, 0) / 8;
        return avg < 0.95 ? SignDetector._ratioConf(0.95 - avg, 0, 0.45) * 0.78 : 0;
      },
    },
    {
      name: 'Expérience',
      /* Both hands fully open */
      check({ leftHand, rightHand }) {
        if (!leftHand || !rightHand) return 0;
        const fingers = [8,12,16,20];
        const pips    = { 8:6, 12:10, 16:14, 20:18 };
        const rMin = Math.min(...fingers.map(i => SignDetector._extensionScore(rightHand, i, pips[i])));
        const lMin = Math.min(...fingers.map(i => SignDetector._extensionScore(leftHand,  i, pips[i])));
        const openScore = Math.min(rMin, lMin);
        return openScore >= 1.15 ? 0.55 + SignDetector._ratioConf(openScore, 1.15, 1.6) * 0.3 : 0;
      },
    },
    {
      name: 'Formation',
      /* V sign — index + middle up, others down */
      check({ rightHand }) {
        if (!rightHand) return 0;
        const eIndex  = SignDetector._extensionScore(rightHand, 8, 6);
        const eMiddle = SignDetector._extensionScore(rightHand, 12, 10);
        const eRing   = SignDetector._extensionScore(rightHand, 16, 14);
        const ePinky  = SignDetector._extensionScore(rightHand, 20, 18);
        if (eIndex < 1.2 || eMiddle < 1.2 || eRing > 1.05 || ePinky > 1.05) return 0;
        const vConf = Math.min(eIndex, eMiddle) - Math.max(eRing, ePinky);
        return SignDetector._ratioConf(vConf, 0.1, 0.7) * 0.82;
      },
    },
    {
      name: 'Comprendre',
      /* Index pointing near head */
      check({ rightHand, pose }) {
        if (!rightHand || !pose) return 0;
        const indexTip    = rightHand[8];
        const nose        = pose[0];
        const indexScore  = SignDetector._extensionScore(rightHand, 8, 6);
        const middleScore = SignDetector._extensionScore(rightHand, 12, 10);
        if (indexScore < 1.2 || middleScore > 1.1) return 0;
        const dist = Math.hypot(indexTip.x - nose.x, indexTip.y - nose.y);
        return SignDetector._ratioConf(0.14 - dist, 0, 0.14) * 0.82;
      },
    },
    {
      name: 'Répéter',
      /* Open hand at mid-torso height */
      check({ rightHand }) {
        if (!rightHand) return 0;
        const wrist = rightHand[0];
        const eIndex = SignDetector._extensionScore(rightHand, 8, 6);
        const eMiddle= SignDetector._extensionScore(rightHand, 12, 10);
        if (eIndex < 1.15 || eMiddle < 1.15) return 0;
        const inZone = wrist.y > 0.33 && wrist.y < 0.58;
        return inZone ? 0.58 + SignDetector._ratioConf(0.12 - Math.abs(wrist.y - 0.45), 0, 0.12) * 0.2 : 0;
      },
    },
    {
      name: 'Question',
      /* Index tip droops below MCP (hooked) */
      check({ rightHand }) {
        if (!rightHand) return 0;
        const indexMCP = rightHand[5];
        const indexPIP = rightHand[6];
        const indexTip = rightHand[8];
        if (!indexMCP || !indexPIP || !indexTip) return 0;
        const droop = indexTip.y - indexMCP.y;
        return SignDetector._ratioConf(droop, 0.02, 0.12) * 0.78;
      },
    },
    {
      name: 'Compétence',
      /* Thumb up, other fingers fisted */
      check({ rightHand }) {
        if (!rightHand) return 0;
        const thumbTip = rightHand[4];
        const thumbIP  = rightHand[3];
        const thumbsUp = thumbTip.y < thumbIP.y - 0.02;
        const fingersCurl = [8,12,16,20].map(i => SignDetector._extensionScore(rightHand, i, {8:6,12:10,16:14,20:18}[i]));
        const avgCurl = fingersCurl.reduce((a, b) => a + b, 0) / fingersCurl.length;
        if (!thumbsUp || avgCurl > 1.0) return 0;
        const thumbLift = SignDetector._ratioConf(thumbIP.y - thumbTip.y, 0.02, 0.15);
        const curlConf  = SignDetector._ratioConf(1.0 - avgCurl, 0, 0.5);
        return 0.55 + (thumbLift + curlConf) / 2 * 0.35;
      },
    },
    {
      name: 'Équipe',
      /* Both wrists close together */
      check({ leftHand, rightHand }) {
        if (!leftHand || !rightHand) return 0;
        const lWrist = leftHand[0];
        const rWrist = rightHand[0];
        const dist = Math.hypot(lWrist.x - rWrist.x, lWrist.y - rWrist.y);
        return SignDetector._ratioConf(0.18 - dist, 0, 0.18) * 0.8;
      },
    },
    {
      name: 'Futur',
      /* Open hand, wrist on right side of frame */
      check({ rightHand }) {
        if (!rightHand) return 0;
        const wrist  = rightHand[0];
        const eIndex = SignDetector._extensionScore(rightHand, 8, 6);
        const eMiddle= SignDetector._extensionScore(rightHand, 12, 10);
        if (eIndex < 1.15 || eMiddle < 1.15) return 0;
        return SignDetector._ratioConf(wrist.x - 0.55, 0, 0.3) * 0.78;
      },
    },
  ];

  /* ── Geometric helpers ── */

  /* Extension score 0-1 for a single finger (tip vs pip joint).
     Uses 3-D distance so it works regardless of hand orientation. */
  static _extensionScore(hand, tipIdx, pipIdx) {
    const tip  = hand[tipIdx];
    const pip  = hand[pipIdx];
    const wrist = hand[0];
    if (!tip || !pip || !wrist) return 0;
    const dTip = Math.hypot(tip.x - wrist.x, tip.y - wrist.y, (tip.z || 0) - (wrist.z || 0));
    const dPip = Math.hypot(pip.x - wrist.x, pip.y - wrist.y, (pip.z || 0) - (wrist.z || 0));
    return dPip > 0 ? Math.min(dTip / dPip, 2) : 0;
  }

  /* Returns true if all listed tip landmarks are extended (score > threshold). */
  static _fingerExtended(hand, indices, threshold = 1.15) {
    const pairs = { 8: 6, 12: 10, 16: 14, 20: 18, 4: 2 };
    return indices.every(i => {
      const pipIdx = pairs[i] ?? (i - 2);
      return SignDetector._extensionScore(hand, i, pipIdx) >= threshold;
    });
  }

  /* Returns true if all listed tips are curled toward the palm. */
  static _isFist(hand, indices = [8,12,16,20]) {
    return indices.every(i => {
      const pairs = { 8: 6, 12: 10, 16: 14, 20: 18 };
      const pipIdx = pairs[i] ?? (i - 2);
      return SignDetector._extensionScore(hand, i, pipIdx) < 1.0;
    });
  }

  /* Continuous confidence from a geometric ratio (0-1 range). */
  static _ratioConf(value, min, max) {
    if (value <= min) return 0;
    if (value >= max) return 1;
    return (value - min) / (max - min);
  }

  /* ── Classify current landmarks ── */
  _classify(landmarks) {
    /* 1. Trained ML model takes priority when available */
    if (window._signTrainer?.ready) {
      const ml = window._signTrainer.predict(landmarks);
      if (ml) return ml;
    }

    /* 2. Gesture model — landmark-based gesture categorisation + contextual
          disambiguation. Covers all 14 signs without additional model loading. */
    if (window.GestureModel) {
      const gr = GestureModel.classify(landmarks);
      if (gr && gr.confidence >= 0.62) return gr;
    }

    /* 3. Fine-grained geometric rule fallback */
    let best = null, bestConf = 0;
    for (const sign of SignDetector.SIGNS) {
      const conf = sign.check(landmarks);
      if (conf > bestConf) { bestConf = conf; best = sign.name; }
    }
    return bestConf >= this.MIN_CONFIDENCE ? { sign: best, confidence: bestConf } : null;
  }

  /* ── Stabilise with rolling buffer ── */
  _stabilise(result) {
    this.signBuffer.push(result ? result.sign : null);
    if (this.signBuffer.length > this.BUFFER_SIZE) this.signBuffer.shift();

    const counts = {};
    this.signBuffer.forEach(s => { if (s) counts[s] = (counts[s] || 0) + 1; });
    const top = Object.entries(counts).sort((a, b) => b[1] - a[1])[0];

    if (top && top[1] >= Math.ceil(this.BUFFER_SIZE * 0.6)) {
      return top[0];
    }
    return null;
  }

  /* ── MediaPipe results callback ── */
  _onResults(results) {
    const { width, height } = this.canvas;
    this.ctx.clearRect(0, 0, width, height);

    /* Draw skeleton overlay */
    if (results.poseLandmarks) {
      drawConnectors(this.ctx, results.poseLandmarks, POSE_CONNECTIONS,
        { color: 'rgba(6,182,212,.4)', lineWidth: 1 });
    }
    if (results.leftHandLandmarks) {
      drawConnectors(this.ctx, results.leftHandLandmarks, HAND_CONNECTIONS,
        { color: 'rgba(124,58,237,.8)', lineWidth: 2 });
      drawLandmarks(this.ctx, results.leftHandLandmarks,
        { color: '#7C3AED', lineWidth: 1, radius: 3 });
    }
    if (results.rightHandLandmarks) {
      drawConnectors(this.ctx, results.rightHandLandmarks, HAND_CONNECTIONS,
        { color: 'rgba(6,182,212,.8)', lineWidth: 2 });
      drawLandmarks(this.ctx, results.rightHandLandmarks,
        { color: '#06B6D4', lineWidth: 1, radius: 3 });
    }

    /* Store current raw landmarks for transmission */
    this._currentLandmarks = {
      rightHand: results.rightHandLandmarks || null,
      leftHand: results.leftHandLandmarks || null,
      pose: results.poseLandmarks || null,
    };

    /* Raw frame hook — used by SignTrainer for data collection */
    if (this.onFrame) this.onFrame(this._currentLandmarks);

    /* Classify */
    const result = this._classify(this._currentLandmarks);

    const stableSign = this._stabilise(result);
    if (stableSign && stableSign !== this.lastSign) {
      this.lastSign = stableSign;
      const conf = result ? result.confidence : this.MIN_CONFIDENCE;
      this.onSign(stableSign, conf, this._currentLandmarks);
    }

    /* Reset if no hands visible for a moment */
    if (!results.leftHandLandmarks && !results.rightHandLandmarks) {
      if (this.signBuffer.every(s => s === null)) this.lastSign = null;
    }
  }

  /* ── Public API ── */
  async start() {
    if (!window.Holistic) {
      console.warn('[SignDetector] MediaPipe not loaded — demo mode');
      this._runDemoMode();
      return;
    }

    this.holistic = new Holistic({
      locateFile: file => `https://cdn.jsdelivr.net/npm/@mediapipe/holistic/${file}`,
    });

    this.holistic.setOptions({
      modelComplexity: 1,
      smoothLandmarks: true,
      enableSegmentation: false,
      refineFaceLandmarks: false,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5,
    });

    this.holistic.onResults(r => {
      this.canvas.width = this.video.videoWidth || this.canvas.offsetWidth;
      this.canvas.height = this.video.videoHeight || this.canvas.offsetHeight;
      this._onResults(r);
    });

    this.camera = new Camera(this.video, {
      onFrame: async () => {
        if (this.active) await this.holistic.send({ image: this.video });
      },
      width: 640,
      height: 480,
    });

    this.active = true;
    await this.camera.start();
  }

  stop() {
    this.active = false;
    if (this.camera) this.camera.stop();
    if (this.holistic) this.holistic.close();
    if (this._demoTimer) clearInterval(this._demoTimer);
  }

  /* Simulate sign detection for demo/testing purposes */
  _runDemoMode() {
    const demoSigns = ['Bonjour', 'Je / Moi', 'Travail', 'Expérience', 'Compétence', 'Oui', 'Merci'];
    let i = 0;
    this._demoTimer = setInterval(() => {
      if (!this.active) return;
      const sign = demoSigns[i % demoSigns.length];
      const conf = 0.75 + Math.random() * 0.2;
      this.onSign(sign, conf, null);
      i++;
    }, 4000);
    this.active = true;
  }

  setActive(value) {
    this.active = value;
    if (!value) {
      this.lastSign = null;
      this.signBuffer = [];
    }
  }
}

window.SignDetector = SignDetector;
