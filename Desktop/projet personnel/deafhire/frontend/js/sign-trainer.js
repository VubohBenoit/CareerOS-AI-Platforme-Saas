/* =========================================================
   DeafHire — Sign Trainer (TensorFlow.js)
   Entraîne un réseau de neurones MLP en local dans le navigateur
   à partir d'exemples enregistrés par l'utilisateur.

   Pipeline :
     MediaPipe landmarks → normalisation → MLP → classe LSF

   Persistance : dataset + poids du modèle sauvegardés en
   localStorage, rechargés automatiquement à chaque session.
   ========================================================= */

'use strict';

class SignTrainer {

  static CLASSES = [
    'Bonjour', 'Merci', 'Oui', 'Non', 'Je / Moi',
    'Travail', 'Expérience', 'Formation', 'Comprendre',
    'Répéter', 'Question', 'Compétence', 'Équipe', 'Futur',
  ];

  /*
    Guide visuel par signe.
    fingers : [pouce, index, majeur, annulaire, auriculaire]
              1 = doigt tendu, 0 = doigt replié, 0.5 = courbé/partiel
    both    : true si les DEUX mains sont utilisées
    desc    : instruction claire pour l'utilisateur
    pos     : position de la main ('front' = niveau front, 'chin' = menton,
              'chest' = poitrine, 'mid' = mi-corps, 'right' = côté droit)
  */
  static SIGN_GUIDES = {
    'Bonjour':    { fingers:[1,1,1,1,1], both:false, pos:'front',
                    desc:'Main ouverte, paume vers vous, au niveau du front. Éloignez légèrement vers l\'extérieur.' },
    'Merci':      { fingers:[1,1,1,1,1], both:false, pos:'chin',
                    desc:'Main plate, paume vers le bas, partez du menton vers l\'avant.' },
    'Oui':        { fingers:[0,0,0,0,0], both:false, pos:'mid',
                    desc:'Poing fermé, effectuez un mouvement de hochement (haut ↔ bas).' },
    'Non':        { fingers:[0,1,0,0,0], both:false, pos:'mid',
                    desc:'Seul l\'index est tendu. Agitez latéralement (gauche ↔ droite).' },
    'Je / Moi':   { fingers:[0,1,0,0,0], both:false, pos:'chest',
                    desc:'Index pointé vers votre poitrine.' },
    'Travail':    { fingers:[0,0,0,0,0], both:true,  pos:'mid',
                    desc:'Les deux poings fermés, tapez-les l\'un contre l\'autre devant vous.' },
    'Expérience': { fingers:[1,1,1,1,1], both:true,  pos:'mid',
                    desc:'Les deux mains grandes ouvertes, doigts écartés, paumes vers vous.' },
    'Formation':  { fingers:[0,1,1,0,0], both:false, pos:'mid',
                    desc:'Signe V : index et majeur tendus, autres doigts repliés.' },
    'Comprendre': { fingers:[0,1,0,0,0], both:false, pos:'front',
                    desc:'Index tendu, touchez légèrement votre tempe.' },
    'Répéter':    { fingers:[0,1,1,0,0], both:false, pos:'mid',
                    desc:'Main semi-ouverte à mi-hauteur, effectuez un mouvement circulaire.' },
    'Question':   { fingers:[0,0.5,0,0,0], both:false, pos:'mid',
                    desc:'Index courbé en crochet (forme de ? inversé), paume vers l\'avant.' },
    'Compétence': { fingers:[0.5,0,0,0,0], both:false, pos:'mid',
                    desc:'Pouce levé, les quatre autres doigts repliés en poing.' },
    'Équipe':     { fingers:[1,1,1,1,1], both:true,  pos:'mid',
                    desc:'Les deux poignets rapprochés devant vous, mains jointes ou croisées.' },
    'Futur':      { fingers:[1,1,1,1,1], both:false, pos:'right',
                    desc:'Main ouverte, poussez vers l\'avant et vers la droite du cadre.' },
  };

  /* Génère un SVG minimaliste représentant la configuration de la main */
  static drawHandSVG(signName, size = 80) {
    const guide = SignTrainer.SIGN_GUIDES[signName];
    if (!guide) return '';

    const f = guide.fingers; // [pouce, index, majeur, annulaire, auriculaire]
    const w = size, h = Math.round(size * 1.2);
    const palmY = Math.round(h * 0.55);
    const palmH = Math.round(h * 0.35);
    const palmX = Math.round(w * 0.18);
    const palmW = Math.round(w * 0.64);

    // Finger dimensions (x center, max height)
    const fingerDefs = [
      { cx: palmX + palmW * 0.08, maxH: palmY * 0.55, w: palmW * 0.16 },  // pouce (angled)
      { cx: palmX + palmW * 0.25, maxH: palmY * 0.72, w: palmW * 0.16 },  // index
      { cx: palmX + palmW * 0.44, maxH: palmY * 0.78, w: palmW * 0.16 },  // majeur
      { cx: palmX + palmW * 0.63, maxH: palmY * 0.72, w: palmW * 0.16 },  // annulaire
      { cx: palmX + palmW * 0.82, maxH: palmY * 0.58, w: palmW * 0.14 },  // auriculaire
    ];

    let fingers = '';
    fingerDefs.forEach((fd, i) => {
      const ext = f[i] ?? 0;           // 0=replié, 0.5=courbé, 1=tendu
      const fh  = Math.round(fd.maxH * (ext >= 1 ? 1 : ext >= 0.5 ? 0.55 : 0.18));
      const fy  = palmY - fh;
      const fw  = Math.round(fd.w);
      const fx  = Math.round(fd.cx - fw / 2);
      const col = ext >= 1 ? '#06B6D4' : ext >= 0.5 ? '#A78BFA' : '#374151';
      const rx  = Math.round(fw / 2);
      fingers += `<rect x="${fx}" y="${fy}" width="${fw}" height="${fh + Math.round(palmH * 0.3)}" rx="${rx}" fill="${col}" opacity="${ext > 0 ? 1 : 0.45}"/>`;
    });

    // Palm
    const palmColor = '#1E293B';
    const palmStroke = '#374151';

    // Both-hands indicator
    const bothHint = guide.both
      ? `<text x="${w/2}" y="${h - 4}" text-anchor="middle" font-size="9" fill="#A78BFA" font-family="sans-serif">deux mains</text>`
      : '';

    return `<svg viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg" style="width:${size}px;height:auto;display:block">
  ${fingers}
  <rect x="${palmX}" y="${palmY}" width="${palmW}" height="${palmH}" rx="${Math.round(palmW*0.18)}" fill="${palmColor}" stroke="${palmStroke}" stroke-width="1.5"/>
  ${bothHint}
</svg>`;
  }

  static MIN_SAMPLES  = 10;   // exemples min par signe pour entraîner
  static DATASET_KEY  = 'dh_sign_dataset_v2';
  static MODEL_KEY    = 'dh_sign_model_v2';

  constructor() {
    this.model    = null;
    this.ready    = false;
    this._classes = [];
    this._dataset = this._loadDataset();
    this._loadModel();        // essaie localStorage d'abord
    this._loadServerModel();  // essaie le grand modèle backend ensuite
  }

  /* ── Extraction de features ──────────────────────────────
     Normalise chaque main :
       • origine → poignet (landmark 0)
       • échelle → distance poignet → MCP majeur (landmark 9)
     Résultat : vecteur 126-dim (21 pts × 3 coords × 2 mains)
     Invariant à la translation et à l'échelle de la main.
  */
  static extract(landmarks) {
    function normHand(hand) {
      const out = new Float32Array(63);
      if (!hand || hand.length < 10) return out;
      const w     = hand[0];
      const ref   = hand[9];
      const scale = Math.hypot(
        ref.x - w.x, ref.y - w.y, (ref.z || 0) - (w.z || 0)
      ) || 1e-6;
      for (let i = 0; i < 21; i++) {
        const p = hand[i] || { x: 0, y: 0, z: 0 };
        out[i * 3]     = (p.x - w.x) / scale;
        out[i * 3 + 1] = (p.y - w.y) / scale;
        out[i * 3 + 2] = ((p.z || 0) - (w.z || 0)) / scale;
      }
      return out;
    }
    const rh  = normHand(landmarks?.rightHand);
    const lh  = normHand(landmarks?.leftHand);
    const out = new Float32Array(126);
    out.set(rh, 0);
    out.set(lh, 63);
    return Array.from(out);
  }

  /* ── Gestion du dataset ─────────────────────────────── */

  record(signName, frames) {
    if (!this._dataset[signName]) this._dataset[signName] = [];
    const valid = frames
      .filter(f => f?.rightHand || f?.leftHand)
      .map(f => SignTrainer.extract(f));
    this._dataset[signName].push(...valid);
    this._saveDataset();
    return this._dataset[signName].length;
  }

  getStats() {
    return SignTrainer.CLASSES.reduce((acc, s) => {
      acc[s] = (this._dataset[s] || []).length;
      return acc;
    }, {});
  }

  clearSign(name) {
    delete this._dataset[name];
    this._saveDataset();
  }

  clearAll() {
    this._dataset = {};
    this._saveDataset();
    this.model = null;
    this.ready = false;
  }

  canTrain() {
    return SignTrainer.CLASSES.filter(
      s => (this._dataset[s] || []).length >= SignTrainer.MIN_SAMPLES
    ).length >= 2;
  }

  totalSamples() {
    return Object.values(this._dataset).reduce((a, arr) => a + arr.length, 0);
  }

  /* ── Entraînement MLP ────────────────────────────────── */

  async train(onProgress) {
    if (!window.tf) throw new Error('TensorFlow.js non chargé');

    const valid = SignTrainer.CLASSES.filter(
      s => (this._dataset[s] || []).length >= SignTrainer.MIN_SAMPLES
    );
    if (valid.length < 2) throw new Error('Minimum 2 signes avec 10 exemples chacun');

    /* Build tensors */
    const X = [], Y = [];
    valid.forEach((sign, idx) => {
      (this._dataset[sign] || []).forEach(feat => { X.push(feat); Y.push(idx); });
    });

    const xs = tf.tensor2d(X, [X.length, 126]);
    const ys = tf.oneHot(tf.tensor1d(Y, 'int32'), valid.length);

    /* Model */
    const model = tf.sequential({ layers: [
      tf.layers.dense({
        inputShape: [126], units: 128, activation: 'relu',
        kernelRegularizer: tf.regularizers.l2({ l2: 1e-4 }),
      }),
      tf.layers.batchNormalization(),
      tf.layers.dropout({ rate: 0.35 }),
      tf.layers.dense({ units: 64, activation: 'relu' }),
      tf.layers.dropout({ rate: 0.2 }),
      tf.layers.dense({ units: valid.length, activation: 'softmax' }),
    ]});

    model.compile({
      optimizer: tf.train.adam(0.001),
      loss:      'categoricalCrossentropy',
      metrics:   ['accuracy'],
    });

    const EPOCHS = 80;
    let lastAcc  = 0;

    await model.fit(xs, ys, {
      epochs:          EPOCHS,
      batchSize:       32,
      validationSplit: 0.15,
      shuffle:         true,
      callbacks: {
        onEpochEnd: (epoch, logs) => {
          lastAcc = logs.val_acc ?? logs.acc ?? 0;
          onProgress?.(epoch + 1, EPOCHS, lastAcc);
        },
      },
    });

    xs.dispose();
    ys.dispose();

    this.model    = model;
    this._classes = valid;
    this.ready    = true;

    await model.save(`localstorage://${SignTrainer.MODEL_KEY}`);
    localStorage.setItem(`${SignTrainer.MODEL_KEY}_cls`, JSON.stringify(valid));

    return { classes: valid, accuracy: lastAcc };
  }

  /* ── Inférence ───────────────────────────────────────── */

  predict(landmarks) {
    if (!this.model || !this.ready || !window.tf) return null;
    const feat  = SignTrainer.extract(landmarks);
    const input = tf.tensor2d([feat], [1, 126]);
    const probs = this.model.predict(input).dataSync();
    input.dispose();
    const maxIdx = probs.indexOf(Math.max(...probs));
    const conf   = probs[maxIdx];
    return conf >= 0.65
      ? { sign: this._classes[maxIdx], confidence: conf }
      : null;
  }

  /* ── Persistance ─────────────────────────────────────── */

  async _loadModel() {
    if (!window.tf) { setTimeout(() => this._loadModel(), 1200); return; }
    try {
      this.model    = await tf.loadLayersModel(`localstorage://${SignTrainer.MODEL_KEY}`);
      const cls     = localStorage.getItem(`${SignTrainer.MODEL_KEY}_cls`);
      this._classes = cls ? JSON.parse(cls) : SignTrainer.CLASSES;
      this.ready    = true;
      console.info(`[SignTrainer] Modèle localStorage restauré — ${this._classes.length} classes`);
    } catch { /* pas de modèle local — normal */ }
  }

  /* Tente de charger le grand modèle entraîné en Python depuis le backend.
     S'il est disponible, il remplace le modèle local (plus de classes). */
  async _loadServerModel() {
    if (!window.tf) { setTimeout(() => this._loadServerModel(), 2000); return; }
    try {
      const API = (typeof Auth !== 'undefined' && Auth.API_BASE)
        ? Auth.API_BASE
        : (location.port === '5500' || location.port === '5501')
          ? 'http://localhost:8001'
          : location.origin;

      const status = await fetch(`${API}/model/status`).then(r => r.json()).catch(() => null);
      if (!status?.available) return;

      console.info(`[SignTrainer] Grand modèle disponible — ${status.n_classes} signes (${status.size_mb} MB)`);

      const [model, classes] = await Promise.all([
        tf.loadLayersModel(`${API}/model/tfjs/model.json`),
        fetch(`${API}/model/classes`).then(r => r.json()),
      ]);

      this.model    = model;
      this._classes = classes;
      this.ready    = true;
      this._serverModel = true;
      console.info(`[SignTrainer] Grand modèle chargé — ${classes.length} signes LSF`);

      /* Met à jour le badge IA dans l'interface si présent */
      const badge = document.getElementById('ai-badge');
      const txt   = document.getElementById('trainer-status-text');
      const dot   = document.getElementById('trainer-dot');
      if (badge) badge.style.display = 'inline';
      if (txt)   txt.textContent = `Grand modèle actif — ${classes.length} signes LSF`;
      if (dot)   dot.className = 'trainer-dot trainer-dot--active';

    } catch (e) {
      /* Grand modèle absent ou backend hors ligne — silencieux */
    }
  }

  _loadDataset() {
    try { return JSON.parse(localStorage.getItem(SignTrainer.DATASET_KEY) || '{}'); }
    catch { return {}; }
  }

  _saveDataset() {
    try { localStorage.setItem(SignTrainer.DATASET_KEY, JSON.stringify(this._dataset)); }
    catch { console.warn('[SignTrainer] localStorage plein — données non sauvegardées'); }
  }
}

window.SignTrainer = SignTrainer;
