/* =========================================================
   DeafHire — WebSocket Client
   Connects to the FastAPI backend for real-time translation.
   Falls back to demo mode when backend is unavailable.
   ========================================================= */

'use strict';

class WSClient {
  constructor(sessionId, role) {
    this.sessionId = sessionId;
    this.role      = role;
    this.ws        = null;
    this.connected = false;
    this.demoMode  = false;
    this.listeners = {};

    this._connectTimeout  = null;
    this._pingInterval    = null;
    this._reconnectDelay  = 2000;
    this._maxReconnects   = 5;
    this._reconnects      = 0;
  }

  connect(wsUrl = this._defaultWsUrl()) {
    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.connected = true;
        this._reconnects = 0;
        clearTimeout(this._connectTimeout);
        this._startKeepalive();
        this._emit('connected');
        console.log('[WSClient] Connected to', wsUrl);
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this._emit('message', data);
          if (data.type !== 'pong') this._emit(data.type, data);
        } catch {
          this._emit('message', { type: 'raw', payload: event.data });
        }
      };

      this.ws.onerror = () => {
        console.warn('[WSClient] Connection error — switching to demo mode');
        this._switchToDemo();
      };

      this.ws.onclose = () => {
        this.connected = false;
        this._stopKeepalive();
        this._emit('disconnected');
        if (this._reconnects < this._maxReconnects && !this.demoMode) {
          this._reconnects++;
          const delay = this._reconnectDelay * this._reconnects;
          console.log(`[WSClient] Reconnecting in ${delay}ms (attempt ${this._reconnects})`);
          setTimeout(() => this.connect(wsUrl), delay);
        }
      };

      /* Switch to demo if no connection after 3s */
      this._connectTimeout = setTimeout(() => {
        if (!this.connected) this._switchToDemo();
      }, 3000);

    } catch {
      this._switchToDemo();
    }
  }

  _switchToDemo() {
    clearTimeout(this._connectTimeout);
    if (this.demoMode) return;
    this.demoMode = true;
    this._emit('demo-mode');
    console.info('[WSClient] Demo mode active — no backend required');
  }

  /* Keep WebSocket alive with a ping every 25s */
  _startKeepalive() {
    this._pingInterval = setInterval(() => {
      if (this.connected && this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 25000);
  }

  _stopKeepalive() {
    clearInterval(this._pingInterval);
    this._pingInterval = null;
  }

  /* Send any message */
  send(type, payload) {
    if (this.demoMode) {
      this._emit('message', { type, payload });
      return;
    }
    if (this.connected && this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, payload }));
    }
  }

  /* Send detected sign + raw landmarks for server-side translation */
  sendKeypoints(sign, confidence = 0.75, landmarks = {}) {
    if (this.demoMode) {
      const SIGN_TO_TEXT = {
        'Bonjour':    'Bonjour, je suis ravi(e) de vous rencontrer.',
        'Merci':      "Merci pour cette opportunité.",
        'Oui':        'Oui, absolument.',
        'Non':        "Non, ce n'est pas le cas.",
        'Je / Moi':   'Je me présente.',
        'Travail':    "J'ai de l'expérience dans ce domaine.",
        'Expérience': "J'ai plusieurs années d'expérience.",
        'Formation':  "J'ai suivi une formation spécialisée.",
        'Comprendre': "J'ai bien compris votre question.",
        'Répéter':    "Pourriez-vous répéter s'il vous plaît ?",
        'Question':   "J'ai une question à vous poser.",
        'Compétence': "C'est l'une de mes compétences clés.",
        'Équipe':     "J'apprécie le travail en équipe.",
        'Futur':      "À terme, je souhaite évoluer.",
      };
      const text = SIGN_TO_TEXT[sign] || `[Signe : ${sign}]`;
      setTimeout(() => this._emit('sign_translation', {
        type: 'sign_translation',
        payload: { sign, text, confidence, latency_ms: 45 },
      }), 80);
      return;
    }
    this.send('sign_keypoints', { sign, confidence, keypoints: landmarks, timestamp: Date.now() });
  }

  /* Send recruiter text message */
  sendRecruiterMessage(text) {
    this.send('recruiter_message', { text, timestamp: Date.now() });
  }

  /* WebRTC signaling relay */
  sendWebRTC(type, payload) {
    /* In demo mode, loop back to self so single-tab testing works */
    if (this.demoMode) {
      setTimeout(() => this._emit(type, { type, payload }), 100);
      return;
    }
    this.send(type, payload);
  }

  /* Event emitter */
  on(event, callback) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(callback);
    return this;
  }

  off(event, callback) {
    if (!this.listeners[event]) return;
    this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
  }

  _emit(event, data) {
    (this.listeners[event] || []).forEach(cb => cb(data));
  }

  disconnect() {
    this._stopKeepalive();
    clearTimeout(this._connectTimeout);
    if (this.ws) this.ws.close();
  }

  _defaultWsUrl() {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
    if (location.port === '5500' || location.port === '5501') {
      return `ws://localhost:8001/ws/${this.sessionId}/${this.role}`;
    }
    return `${protocol}//${location.host}/ws/${this.sessionId}/${this.role}`;
  }
}

window.WSClient = WSClient;
