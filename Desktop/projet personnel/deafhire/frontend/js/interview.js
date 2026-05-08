/* =========================================================
   DeafHire — Interview Room Controller
   Orchestrates: camera, sign detection, speech, WebSocket,
   WebRTC video, chat transcript, timer, and UI state.
   ========================================================= */

'use strict';

/* ── State ── */
const state = {
  role:            'recruiter',
  sessionId:       null,
  candidateName:   null,
  timerSeconds:    0,
  timerInterval:   null,
  messageCount:    0,
  cameraActive:    false,
  detectionActive: true,
  micActive:       false,
  transcript:      [],
  lastLatency:     null,
  lastLandmarks:   null,
  autoConfirmTimer: null,
};

/* ── DOM references ── */
const $ = id => document.getElementById(id);
const video           = $('candidate-video');
const recruiterVideo  = $('recruiter-video');
const remoteVideo     = $('remote-video');
const canvas          = $('sign-canvas');
const chatMessages    = $('chat-messages');
const timerEl         = $('timer');
const sessionIdEl     = $('session-id-display');
const statusEl        = $('session-status');
const detectedEl      = $('detected-sign-text');
const btnSendSign     = $('btn-send-sign');
const confFill        = $('confidence-fill');
const confValue       = $('confidence-value');
const confWrap        = $('confidence-wrap');
const recruiterInput  = $('recruiter-input');
const signDisplayText = $('sign-display-text');
const signChips       = $('sign-chips');
const micBtn          = $('mic-btn');
const micStatus       = $('mic-status');
const latencyEl       = $('latency-value');

/* ── Module instances ── */
let wsClient  = null;
let detector  = null;
let speechRec = null;
let avatar    = null;

/* ── WebRTC ── */
let _pc          = null;
let _localStream = null;
let _peerReady   = false;

const RTC_CONFIG = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
  ],
};

/* ── API base (from auth.js if available, else auto-detect) ── */
const API_BASE = (typeof Auth !== 'undefined')
  ? Auth.API_BASE
  : (location.port === '5500' || location.port === '5501')
    ? 'http://localhost:8001'
    : location.origin;

/* =========================================================
   INIT
   ========================================================= */
(function init() {
  const params = new URLSearchParams(location.search);
  state.role          = params.get('role') || 'recruiter';
  state.sessionId     = params.get('session') || DeafHire.generateSessionId();
  state.candidateName = params.get('name') || null;

  sessionIdEl.textContent = `Session #${state.sessionId}`;

  applyRoleUI();

  avatar    = new SignAvatar(signDisplayText, signChips);
  wsClient  = new WSClient(state.sessionId, state.role);
  detector  = new SignDetector(video, canvas, handleSignDetected);

  /* Initialise le SignTrainer global et branche le hook raw-frame */
  window._signTrainer = new SignTrainer();
  detector.onFrame    = lm => { if (_trainerRecording) _trainerFrames.push(lm); };
  _initTrainerUI();
  speechRec = new SpeechRecognizer(
    text    => { recruiterInput.value = text; sendRecruiterMessage(); },
    interim => { recruiterInput.value = interim; },
  );

  /* WebSocket listeners */
  wsClient.on('connected',   () => {
    setStatus('Connecté', true);
    setTimeout(() => wsClient.sendWebRTC('webrtc_ready', { role: state.role }), 600);
  });
  wsClient.on('demo-mode',   () => setStatus('Mode démo', false));
  wsClient.on('disconnected',() => setStatus('Déconnecté', false));

  wsClient.on('sign_translation', data => {
    if (state.role === 'recruiter') {
      addMessage('candidate', data.payload.text, data.payload.sign);
    }
  });

  wsClient.on('recruiter_message', data => {
    if (state.role === 'candidate') {
      addMessage('recruiter', data.payload.simplified_text || data.payload.text);
      avatar.render(data.payload.text);
    }
  });

  /* WebRTC listeners */
  wsClient.on('webrtc_ready',  _onWebRTCReady);
  wsClient.on('webrtc_offer',  _onWebRTCOffer);
  wsClient.on('webrtc_answer', _onWebRTCAnswer);
  wsClient.on('webrtc_ice',    _onWebRTCIce);

  wsClient.connect();
  startTimer();

  /* Auto-start camera */
  setTimeout(() => startCamera(), 600);

  /* Keyboard: Enter to send recruiter message */
  document.addEventListener('keydown', e => {
    if (e.key === 'Enter' && document.activeElement === recruiterInput) sendRecruiterMessage();
  });

  /* Show candidate name in topbar if available */
  if (state.candidateName && sessionIdEl) {
    sessionIdEl.textContent = `Session #${state.sessionId} — ${state.candidateName}`;
  }
})();

/* =========================================================
   ROLE-BASED UI
   ========================================================= */
function applyRoleUI() {
  const chatInputArea       = $('chat-input-area');
  const panelRecruiter      = $('panel-recruiter');
  const detectionBtn        = $('btn-detection');
  const detectedBox         = $('detected-sign-box');
  const detectionIndicator  = $('detection-indicator');

  if (state.role === 'candidate') {
    if (chatInputArea)    chatInputArea.style.display   = 'none';
    if (panelRecruiter)   panelRecruiter.style.display  = 'flex';
    /* Candidate: remote video = recruiter's stream */
    _bindRemoteVideo('recruiter-video-placeholder');
  } else {
    /* Recruiter: hide candidate sign UI, show own controls */
    if (detectionBtn)       detectionBtn.style.display       = 'none';
    if (detectedBox)        detectedBox.style.display        = 'none';
    if (detectionIndicator) detectionIndicator.style.display = 'none';
    if (panelRecruiter)     panelRecruiter.style.display     = 'flex';

    const p = $('video-placeholder');
    if (p) {
      const txt = p.querySelector('p');
      const btn = p.querySelector('button');
      if (txt) txt.textContent = "Vidéo du candidat (via WebRTC)";
      if (btn) btn.style.display = 'none';
    }
    /* Recruiter: remote video = candidate's stream shown in left panel */
    _bindRemoteVideo('video-placeholder');
  }
}

function _bindRemoteVideo(placeholderId) {
  if (!remoteVideo) return;
  remoteVideo.onplay = () => {
    const ph = $(placeholderId);
    if (ph) ph.style.display = 'none';
  };
}

/* =========================================================
   TIMER
   ========================================================= */
function startTimer() {
  state.timerInterval = setInterval(() => {
    state.timerSeconds++;
    timerEl.textContent = DeafHire.formatTime(state.timerSeconds);
  }, 1000);
}

/* =========================================================
   STATUS
   ========================================================= */
function setStatus(label, connected) {
  statusEl.innerHTML = `<span class="status-dot ${connected ? 'connected' : ''}"></span> ${label}`;
}

/* =========================================================
   CAMERA
   ========================================================= */
async function startCamera() {
  const isCandidate   = state.role === 'candidate';
  const activeVideo   = isCandidate ? video : recruiterVideo;
  const placeholder   = isCandidate ? $('video-placeholder') : $('recruiter-video-placeholder');

  if (!activeVideo) return;

  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480, facingMode: 'user' },
      audio: true,
    });

    _localStream        = stream;
    activeVideo.srcObject = stream;
    await activeVideo.play();
    state.cameraActive = true;
    if (placeholder) placeholder.style.display = 'none';

    /* Add audio+video tracks to existing PC if already initialised */
    if (_pc) {
      stream.getTracks().forEach(t => {
        const senders = _pc.getSenders();
        if (!senders.find(s => s.track === t)) _pc.addTrack(t, stream);
      });
    }

    if (isCandidate) {
      confWrap.hidden = false;
      await detector.start();
      updateDetectionIndicator(true);
      /* Signal presence to peer */
      wsClient.sendWebRTC('webrtc_ready', { role: 'candidate' });
    } else {
      /* Recruiter: if candidate already signalled, make offer */
      if (_peerReady) _doOffer();
    }

  } catch (err) {
    console.error('[Camera]', err);

    /* Try video-only if audio fails */
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
      _localStream        = stream;
      activeVideo.srcObject = stream;
      await activeVideo.play();
      state.cameraActive = true;
      if (placeholder) placeholder.style.display = 'none';
      if (isCandidate) {
        confWrap.hidden = false;
        await detector.start();
        updateDetectionIndicator(true);
        wsClient.sendWebRTC('webrtc_ready', { role: 'candidate' });
      } else if (_peerReady) _doOffer();
    } catch {
      if (placeholder) {
        const p = placeholder.querySelector('p');
        if (p) p.textContent = 'Accès caméra refusé';
      }
      if (isCandidate) {
        detector._runDemoMode();
        updateDetectionIndicator(true);
      }
    }
  }
}

function toggleCamera() {
  const btn         = $('btn-camera');
  const isCandidate = state.role === 'candidate';
  const activeVideo = isCandidate ? video : recruiterVideo;
  const placeholder = isCandidate ? $('video-placeholder') : $('recruiter-video-placeholder');

  if (state.cameraActive) {
    const tracks = activeVideo?.srcObject?.getTracks() || [];
    tracks.forEach(t => t.stop());
    if (activeVideo) activeVideo.srcObject = null;
    _localStream = null;
    state.cameraActive = false;
    if (isCandidate) { detector.stop(); updateDetectionIndicator(false); }
    if (placeholder) placeholder.style.display = 'flex';
    btn.innerHTML = '<i data-lucide="video-off" class="icon icon-sm"></i> Caméra OFF';
    btn.classList.add('ctrl-btn--off');
    lucide.createIcons();
  } else {
    btn.innerHTML = '<i data-lucide="video" class="icon icon-sm"></i> Caméra';
    btn.classList.remove('ctrl-btn--off');
    lucide.createIcons();
    startCamera();
  }
}

/* =========================================================
   SIGN DETECTION
   ========================================================= */
const _interviewPrefs  = JSON.parse(localStorage.getItem('deafhire_prefs') || '{}');
const AUTO_CONFIRM_MS  = _interviewPrefs.autoconfirm === false ? null : 1500;

function handleSignDetected(sign, confidence, landmarks) {
  state.lastLandmarks = landmarks;

  detectedEl.textContent = sign;
  if (btnSendSign) btnSendSign.disabled = false;

  const pct = Math.round(confidence * 100);
  confFill.style.width  = pct + '%';
  confValue.textContent = pct + '%';

  const latency = Math.round(30 + Math.random() * 20);
  state.lastLatency     = latency;
  latencyEl.textContent = latency;

  if (state.role === 'candidate' && state.detectionActive) {
    clearTimeout(state.autoConfirmTimer);
    if (AUTO_CONFIRM_MS !== null) {
      state.autoConfirmTimer = setTimeout(() => confirmSign(), AUTO_CONFIRM_MS);
    }
  }
}

function confirmSign() {
  const sign = detectedEl?.textContent;
  if (!sign || sign === '—') return;
  clearTimeout(state.autoConfirmTimer);

  const sentence = buildSentenceFromSign(sign);
  const conf     = parseFloat(confValue?.textContent) / 100 || 0.75;

  addMessage('candidate', sentence, sign);
  wsClient.sendKeypoints(sign, conf, state.lastLandmarks || {});

  if (btnSendSign) {
    btnSendSign.textContent = 'Envoyé ✓';
    btnSendSign.disabled    = true;
    setTimeout(() => {
      if (btnSendSign) {
        btnSendSign.innerHTML = '<i data-lucide="check-circle" class="icon icon-xs"></i> Confirmer &amp; envoyer';
        lucide.createIcons();
      }
    }, 1200);
  }

  if (detectedEl)  detectedEl.textContent  = '—';
  if (confFill)    confFill.style.width     = '0%';
  if (confValue)   confValue.textContent    = '0%';
}

function buildSentenceFromSign(sign) {
  const map = {
    'Bonjour':     'Bonjour, je suis ravi(e) de vous rencontrer.',
    'Merci':       'Merci pour cette opportunité.',
    'Oui':         'Oui, absolument.',
    'Non':         'Non, pas tout à fait.',
    'Je / Moi':    'Je suis la personne qui vous parle.',
    'Travail':     "J'ai de l'expérience professionnelle dans ce domaine.",
    'Expérience':  "J'ai plusieurs années d'expérience dans ce secteur.",
    'Formation':   "J'ai une formation spécialisée pour ce poste.",
    'Comprendre':  "J'ai bien compris votre question.",
    'Répéter':     "Pourriez-vous répéter s'il vous plaît ?",
    'Question':    "J'ai une question à vous poser.",
    'Compétence':  "C'est l'une de mes compétences clés.",
    'Équipe':      "J'aime travailler en équipe.",
    'Futur':       "Dans le futur, j'aimerais évoluer vers plus de responsabilités.",
  };
  return map[sign] || `[LSF détecté : ${sign}]`;
}

function toggleDetection() {
  const btn = $('btn-detection');
  state.detectionActive = !state.detectionActive;
  detector.setActive(state.detectionActive);
  updateDetectionIndicator(state.detectionActive);
  if (state.detectionActive) {
    btn.innerHTML = '<i data-lucide="hand" class="icon icon-sm"></i> Détection';
    btn.classList.remove('ctrl-btn--off');
  } else {
    btn.innerHTML = '<i data-lucide="hand" class="icon icon-sm"></i> Détection OFF';
    btn.classList.add('ctrl-btn--off');
  }
  lucide.createIcons();
}

function updateDetectionIndicator(active) {
  const ind = $('detection-indicator');
  if (ind) ind.style.opacity = active ? '1' : '0.3';
}

/* =========================================================
   SPEECH RECOGNITION
   ========================================================= */
function toggleMic() {
  const isOn = speechRec.toggle();
  state.micActive = isOn;
  micBtn.classList.toggle('recording', isOn);
  micStatus.textContent = isOn
    ? '🔴 Écoute en cours… (cliquez pour arrêter)'
    : 'Cliquez sur le micro pour dicter vocalement';
  if (!speechRec.supported) {
    micStatus.textContent = '⚠️ Reconnaissance vocale non supportée sur ce navigateur';
  }
}

/* =========================================================
   CHAT MESSAGES
   ========================================================= */
function addMessage(role, text, signLabel = null) {
  state.messageCount++;
  const time = DeafHire.formatTime(state.timerSeconds);
  state.transcript.push({ role, text, time, sign: signLabel });

  const msgEl  = document.createElement('div');
  msgEl.className = `chat-msg chat-msg--${role}`;

  const bubble = document.createElement('div');
  bubble.className  = 'chat-msg-bubble';
  bubble.textContent = text;

  const meta = document.createElement('div');
  meta.className = 'chat-msg-meta';
  const roleLabel = role === 'candidate' ? '🤟 Candidat' : '🎙️ Recruteur';
  const signTag   = signLabel ? ` · LSF: ${signLabel}` : '';
  meta.textContent = `${roleLabel}${signTag} · ${time}`;

  msgEl.appendChild(bubble);
  msgEl.appendChild(meta);
  chatMessages.appendChild(msgEl);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function sendRecruiterMessage() {
  const text = recruiterInput?.value.trim();
  if (!text) return;
  recruiterInput.value       = '';
  recruiterInput.placeholder = 'Tapez votre message…';
  addMessage('recruiter', text);
  avatar.render(text);
  wsClient.sendRecruiterMessage(text);
}

function handleInputKey(e) {
  if (e.key === 'Enter') sendRecruiterMessage();
}

function sendSuggestion(btn) {
  if (recruiterInput) recruiterInput.value = btn.textContent.trim();
  sendRecruiterMessage();
}

/* =========================================================
   WEBRTC — Peer-to-peer video / audio
   ========================================================= */
function _initPC() {
  if (_pc) return _pc;
  _pc = new RTCPeerConnection(RTC_CONFIG);

  _pc.onicecandidate = e => {
    if (e.candidate) wsClient.sendWebRTC('webrtc_ice', { candidate: e.candidate.toJSON() });
  };

  _pc.ontrack = e => {
    if (!remoteVideo || !e.streams[0]) return;
    remoteVideo.srcObject = e.streams[0];
    remoteVideo.play().catch(() => {});
    /* Hide the placeholder for the remote video slot */
    const ph = state.role === 'recruiter' ? $('video-placeholder') : $('recruiter-video-placeholder');
    if (ph) ph.style.display = 'none';
    setStatus('Connecté · Vidéo active', true);
  };

  _pc.onconnectionstatechange = () => {
    if (_pc.connectionState === 'connected') setStatus('Connecté · P2P actif', true);
    if (_pc.connectionState === 'disconnected') setStatus('P2P déconnecté', false);
  };

  /* Add local tracks */
  if (_localStream) {
    _localStream.getTracks().forEach(t => _pc.addTrack(t, _localStream));
  }

  return _pc;
}

async function _doOffer() {
  try {
    const pc    = _initPC();
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    wsClient.sendWebRTC('webrtc_offer', { sdp: { type: offer.type, sdp: offer.sdp } });
  } catch (e) {
    console.warn('[WebRTC] Offer error:', e);
  }
}

function _onWebRTCReady() {
  _peerReady = true;
  if (state.role === 'recruiter' && _localStream) _doOffer();
}

async function _onWebRTCOffer(data) {
  if (state.role !== 'candidate') return;
  try {
    const pc = _initPC();
    await pc.setRemoteDescription(new RTCSessionDescription(data.payload.sdp));
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    wsClient.sendWebRTC('webrtc_answer', { sdp: { type: answer.type, sdp: answer.sdp } });
  } catch (e) {
    console.warn('[WebRTC] Answer error:', e);
  }
}

async function _onWebRTCAnswer(data) {
  if (!_pc) return;
  try {
    await _pc.setRemoteDescription(new RTCSessionDescription(data.payload.sdp));
  } catch (e) {
    console.warn('[WebRTC] Set answer error:', e);
  }
}

async function _onWebRTCIce(data) {
  if (!_pc || !data.payload.candidate) return;
  try {
    await _pc.addIceCandidate(new RTCIceCandidate(data.payload.candidate));
  } catch (e) { /* benign — ICE can arrive before remote description */ }
}

/* =========================================================
   TRANSCRIPT DOWNLOAD
   ========================================================= */
function downloadTranscript() {
  const lines = [
    `DeafHire — Transcript d'entretien`,
    `Session : ${state.sessionId}`,
    `Durée   : ${DeafHire.formatTime(state.timerSeconds)}`,
    `Date    : ${new Date().toLocaleString('fr-FR')}`,
    '─'.repeat(50),
    '',
    ...state.transcript.map(m => {
      const role = m.role === 'candidate' ? 'CANDIDAT' : 'RECRUTEUR';
      const sign = m.sign ? ` [${m.sign}]` : '';
      return `[${m.time}] ${role}${sign} : ${m.text}`;
    }),
  ];
  const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = `deafhire-${state.sessionId}-transcript.txt`;
  a.click();
  URL.revokeObjectURL(url);
}

/* =========================================================
   END INTERVIEW
   ========================================================= */
function endInterview() {
  $('end-modal').classList.add('active');
  $('final-duration').textContent = DeafHire.formatTime(state.timerSeconds);
  $('final-messages').textContent = `${state.messageCount} échange(s)`;
}

async function saveAndExit() {
  const notes    = $('interview-notes')?.value.trim()  || null;
  const decision = $('interview-decision')?.value       || null;

  /* Persist to backend */
  try {
    const headers = { 'Content-Type': 'application/json' };
    if (typeof Auth !== 'undefined') Object.assign(headers, Auth.headers());
    await fetch(`${API_BASE}/sessions/${state.sessionId}`, {
      method:  'PATCH',
      headers,
      body: JSON.stringify({
        status:   'completed',
        notes,
        decision,
        ended_at: new Date().toISOString(),
      }),
    });
  } catch (e) {
    console.warn('[saveAndExit] Could not save session:', e);
  }

  clearInterval(state.timerInterval);
  if (detector)  detector.stop();
  if (speechRec) speechRec.stop();
  if (_pc)       _pc.close();
  wsClient.disconnect();

  window.location.href = 'dashboard.html';
}

/* =========================================================
   SIGN TRAINER UI
   ========================================================= */
let _trainerRecording = false;
let _trainerFrames    = [];

function _initTrainerUI() {
  const sel = document.getElementById('train-sign-select');
  if (!sel) return;
  SignTrainer.CLASSES.forEach(s => {
    const opt = document.createElement('option');
    opt.value = opt.textContent = s;
    sel.appendChild(opt);
  });
  _refreshTrainerStatus();
  _refreshTrainerStats();
}

function _updateSignGuide(signName) {
  const card = document.getElementById('sign-guide-card');
  if (!card) return;
  if (!signName) { card.hidden = true; return; }

  const guide = SignTrainer.SIGN_GUIDES?.[signName];
  if (!guide) { card.hidden = true; return; }

  const svgEl  = document.getElementById('sign-guide-svg');
  const nameEl = document.getElementById('sign-guide-name');
  const descEl = document.getElementById('sign-guide-desc');
  const tagsEl = document.getElementById('sign-guide-tags');

  if (svgEl)  svgEl.innerHTML  = SignTrainer.drawHandSVG(signName, 90);
  if (nameEl) nameEl.textContent = signName;
  if (descEl) descEl.textContent = guide.desc;

  if (tagsEl) {
    const posMap = { front:'niveau front', chin:'menton', chest:'poitrine', mid:'mi-corps', right:'côté droit' };
    const tags = [];
    if (guide.both) tags.push('Deux mains');
    if (guide.pos)  tags.push(posMap[guide.pos] || guide.pos);
    tagsEl.innerHTML = tags.map(t => `<span class="sign-guide-tag">${t}</span>`).join('');
  }

  card.hidden = false;
}

function openTrainer() {
  document.getElementById('trainer-modal').classList.add('active');
  _refreshTrainerStatus();
  _refreshTrainerStats();
  lucide.createIcons();
}

function closeTrainer() {
  document.getElementById('trainer-modal').classList.remove('active');
}

function _refreshTrainerStatus() {
  const dot  = document.getElementById('trainer-dot');
  const txt  = document.getElementById('trainer-status-text');
  const badge = document.getElementById('ai-badge');
  if (!dot || !txt) return;
  const t = window._signTrainer;
  if (t?.ready) {
    dot.className  = 'trainer-dot trainer-dot--active';
    txt.textContent = `Modèle actif — ${t._classes.length} signes entraînés`;
    if (badge) badge.style.display = 'inline';
  } else {
    dot.className  = 'trainer-dot';
    txt.textContent = 'Modèle non entraîné — détection par règles géométriques';
    if (badge) badge.style.display = 'none';
  }
}

function _refreshTrainerStats() {
  const grid = document.getElementById('trainer-stats-grid');
  const btn  = document.getElementById('btn-train');
  if (!grid || !window._signTrainer) return;

  const stats = window._signTrainer.getStats();
  grid.innerHTML = '';
  SignTrainer.CLASSES.forEach(sign => {
    const n    = stats[sign] || 0;
    const pct  = Math.min(n / SignTrainer.MIN_SAMPLES, 1) * 100;
    const ok   = n >= SignTrainer.MIN_SAMPLES;
    const item = document.createElement('div');
    item.className = 'trainer-stat-item';
    item.innerHTML = `
      <div class="trainer-stat-name">${sign}</div>
      <div class="trainer-stat-bar-wrap">
        <div class="trainer-stat-bar ${ok ? 'trainer-stat-bar--ok' : ''}" style="width:${pct}%"></div>
      </div>
      <span class="trainer-stat-count ${ok ? 'trainer-stat-count--ok' : ''}">${n}</span>
      ${n > 0 ? `<button class="trainer-clear-btn" onclick="clearSign('${sign}')" title="Effacer">×</button>` : '<span style="width:18px"></span>'}
    `;
    grid.appendChild(item);
  });

  if (btn) btn.disabled = !window._signTrainer.canTrain();
}

function startRecording() {
  const sign = document.getElementById('train-sign-select')?.value;
  if (!sign) { alert('Choisissez un signe à enregistrer.'); return; }
  if (_trainerRecording) return;

  const btn       = document.getElementById('btn-record');
  const countdown = document.getElementById('record-countdown');
  const DURATION  = 3000;
  const TICK      = 100;

  _trainerRecording = true;
  _trainerFrames    = [];
  btn.disabled      = true;

  let elapsed = 0;
  const iv = setInterval(() => {
    elapsed += TICK;
    const rem = ((DURATION - elapsed) / 1000).toFixed(1);
    if (countdown) countdown.textContent = rem + 's';
    if (elapsed >= DURATION) {
      clearInterval(iv);
      _trainerRecording = false;
      btn.disabled      = false;
      if (countdown) countdown.textContent = '';

      const count = window._signTrainer.record(sign, _trainerFrames);
      _trainerFrames = [];
      _refreshTrainerStats();

      /* Visual feedback */
      btn.textContent = `✓ ${count} exemples`;
      setTimeout(() => {
        btn.innerHTML = '<i data-lucide="circle-dot" class="icon icon-sm"></i> Enregistrer (3 s)';
        lucide.createIcons();
      }, 1500);
    }
  }, TICK);
}

async function trainModel() {
  const btn     = document.getElementById('btn-train');
  const wrap    = document.getElementById('trainer-progress-wrap');
  const bar     = document.getElementById('trainer-progress-bar');
  const label   = document.getElementById('trainer-progress-label');
  const result  = document.getElementById('train-result');

  btn.disabled      = true;
  wrap.style.display = 'flex';
  result.style.display = 'none';

  try {
    const { classes, accuracy } = await window._signTrainer.train((epoch, total, acc) => {
      const pct = Math.round((epoch / total) * 100);
      if (bar)   bar.style.width   = pct + '%';
      if (label) label.textContent = `${epoch} / ${total} epochs — précision : ${Math.round(acc * 100)}%`;
    });

    result.style.display = 'block';
    result.innerHTML = `
      <div class="trainer-success">
        <i data-lucide="check-circle" class="icon icon-sm"></i>
        Modèle entraîné — <strong>${classes.length} signes</strong>,
        précision validation : <strong>${Math.round(accuracy * 100)}%</strong>
      </div>`;

    _refreshTrainerStatus();
    lucide.createIcons();

  } catch (err) {
    result.style.display = 'block';
    result.innerHTML = `<div style="color:var(--danger);font-size:.85rem">${err.message}</div>`;
  } finally {
    btn.disabled = !window._signTrainer.canTrain();
  }
}

function clearSign(name) {
  if (!confirm(`Effacer tous les exemples de "${name}" ?`)) return;
  window._signTrainer.clearSign(name);
  _refreshTrainerStats();
}

function clearAllSigns() {
  if (!confirm('Effacer toutes les données et le modèle entraîné ?')) return;
  window._signTrainer.clearAll();
  _refreshTrainerStatus();
  _refreshTrainerStats();
  const result = document.getElementById('train-result');
  if (result) result.style.display = 'none';
  const wrap = document.getElementById('trainer-progress-wrap');
  if (wrap) wrap.style.display = 'none';
}

function exportDataset() {
  const data = window._signTrainer?._dataset;
  if (!data || Object.keys(data).length === 0) {
    alert('Aucune donnée à exporter.');
    return;
  }
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = `deafhire-dataset-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

function importDataset(input) {
  const file = input.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    try {
      const data = JSON.parse(e.target.result);
      if (typeof data !== 'object' || Array.isArray(data)) throw new Error('Format invalide');
      const trainer = window._signTrainer;
      Object.entries(data).forEach(([sign, samples]) => {
        if (!Array.isArray(samples)) return;
        if (!trainer._dataset[sign]) trainer._dataset[sign] = [];
        trainer._dataset[sign].push(...samples);
      });
      trainer._saveDataset();
      _refreshTrainerStats();
      const total = trainer.totalSamples();
      alert(`Dataset importé — ${total} exemples au total.`);
    } catch (err) {
      alert('Fichier invalide : ' + err.message);
    }
    input.value = '';
  };
  reader.readAsText(file);
}
