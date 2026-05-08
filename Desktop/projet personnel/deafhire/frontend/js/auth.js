/* =========================================================
   DeafHire — Auth helper
   Handles JWT storage, login, register, and route guards.
   Falls back to demo mode when backend is unavailable.
   ========================================================= */

'use strict';

const Auth = {
  TOKEN_KEY: 'deafhire_token',
  USER_KEY:  'deafhire_user',
  API_BASE:  (
    location.port === '5500' || location.port === '5501'
      ? 'http://localhost:8001'
      : location.origin
  ),

  /* ── Token storage ── */
  getToken()  { return localStorage.getItem(this.TOKEN_KEY); },
  getUser()   { try { return JSON.parse(localStorage.getItem(this.USER_KEY)); } catch { return null; } },

  isAuthenticated() {
    const token = this.getToken();
    if (!token) return false;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      if (payload.exp * 1000 <= Date.now()) {
        /* Token expired — clean up silently */
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
        return false;
      }
      return true;
    } catch {
      return false;
    }
  },

  /* Auto-redirect when token expires during an active session */
  watchExpiry() {
    const token = this.getToken();
    if (!token) return;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const msLeft  = payload.exp * 1000 - Date.now();
      if (msLeft <= 0) { this.logout(); return; }
      setTimeout(() => {
        alert('Votre session a expiré. Vous allez être redirigé vers la connexion.');
        this.logout();
      }, Math.min(msLeft, 2147483647)); /* clamp to max setTimeout value */
    } catch { /* ignore */ }
  },

  /* ── Login ── */
  async login(email, password) {
    /* Demo mode: accept hardcoded credentials */
    if (email === 'admin@deafhire.fr' && password === 'deafhire2026') {
      this._storeDemoSession(email, 'Recruteur Demo', 'DeafHire');
      return true;
    }

    try {
      const res = await fetch(`${this.API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) return false;
      const data = await res.json();
      localStorage.setItem(this.TOKEN_KEY, data.access_token);
      localStorage.setItem(this.USER_KEY, JSON.stringify(data.user));
      return true;
    } catch {
      /* Backend offline — check demo credentials */
      return false;
    }
  },

  /* ── Register ── */
  async register({ name, email, company, password }) {
    try {
      const res = await fetch(`${this.API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, company, password }),
      });
      if (!res.ok) return false;
      const data = await res.json();
      localStorage.setItem(this.TOKEN_KEY, data.access_token);
      localStorage.setItem(this.USER_KEY, JSON.stringify(data.user));
      return true;
    } catch {
      /* Demo fallback */
      this._storeDemoSession(email, name, company);
      return true;
    }
  },

  /* ── Logout ── */
  logout() {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    window.location.href = 'login.html';
  },

  /* ── Route guard — call at top of protected pages ── */
  requireAuth(redirect = 'login.html') {
    if (!this.isAuthenticated()) {
      window.location.href = redirect;
      return false;
    }
    this.watchExpiry();
    return true;
  },

  /* ── Auth headers for fetch ── */
  headers() {
    const token = this.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  },

  /* ── Demo helpers ── */
  _storeDemoSession(email, name, company) {
    /* Create a fake JWT-like token that expires in 24h */
    const payload = { sub: email, name, company, exp: Math.floor(Date.now() / 1000) + 86400 };
    const fake = `eyJhbGciOiJIUzI1NiJ9.${btoa(JSON.stringify(payload))}.demo`;
    localStorage.setItem(this.TOKEN_KEY, fake);
    localStorage.setItem(this.USER_KEY, JSON.stringify({ email, name, company }));
  },
};

window.Auth = Auth;
