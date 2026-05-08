/* =========================================================
   DeafHire — Global app utilities
   ========================================================= */

'use strict';

const DeafHire = {
  version: '1.0.0',

  /* Parse URL search params */
  getParams() {
    return Object.fromEntries(new URLSearchParams(location.search));
  },

  /* Show a toast notification */
  toast(message, type = 'info', duration = 3000) {
    let el = document.getElementById('toast');
    if (!el) {
      el = document.createElement('div');
      el.id = 'toast';
      el.className = 'toast';
      document.body.appendChild(el);
    }
    el.textContent = message;
    el.className = `toast toast--${type} active`;
    clearTimeout(el._timer);
    el._timer = setTimeout(() => el.classList.remove('active'), duration);
  },

  /* Format seconds to MM:SS */
  formatTime(seconds) {
    const m = String(Math.floor(seconds / 60)).padStart(2, '0');
    const s = String(seconds % 60).padStart(2, '0');
    return `${m}:${s}`;
  },

  /* Generate a short session ID */
  generateSessionId() {
    return 'INT-' + Math.random().toString(36).substring(2, 7).toUpperCase();
  },
};

window.DeafHire = DeafHire;

/* ── Mobile sidebar hamburger ──
   Injected automatically on every dashboard page (body.dashboard-body).
   Creates a toggle button and a backdrop overlay; no HTML changes needed.
*/
document.addEventListener('DOMContentLoaded', () => {
  if (!document.body.classList.contains('dashboard-body')) return;

  const sidebar = document.querySelector('.sidebar');
  if (!sidebar) return;

  /* Hamburger button */
  const btn = document.createElement('button');
  btn.id        = 'sidebar-toggle';
  btn.className = 'sidebar-toggle';
  btn.setAttribute('aria-label', 'Menu');
  btn.innerHTML = '<span></span><span></span><span></span>';
  document.body.appendChild(btn);

  /* Backdrop */
  const backdrop = document.createElement('div');
  backdrop.id        = 'sidebar-backdrop';
  backdrop.className = 'sidebar-backdrop';
  document.body.appendChild(backdrop);

  function openSidebar() {
    sidebar.classList.add('sidebar--open');
    backdrop.classList.add('sidebar-backdrop--active');
    btn.classList.add('sidebar-toggle--open');
  }
  function closeSidebar() {
    sidebar.classList.remove('sidebar--open');
    backdrop.classList.remove('sidebar-backdrop--active');
    btn.classList.remove('sidebar-toggle--open');
  }

  btn.addEventListener('click', () =>
    sidebar.classList.contains('sidebar--open') ? closeSidebar() : openSidebar()
  );
  backdrop.addEventListener('click', closeSidebar);

  /* Close on nav link click (single-page navigations) */
  sidebar.querySelectorAll('.sidebar-link').forEach(a =>
    a.addEventListener('click', closeSidebar)
  );
});

/* Smooth scroll for anchor links */
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', e => {
    const target = document.querySelector(link.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});
