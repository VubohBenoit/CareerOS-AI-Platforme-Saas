/* =========================================================
   DeafHire — Speech Recognition (Recruiter side)
   Wraps the Web Speech API for real-time voice-to-text.
   ========================================================= */

'use strict';

class SpeechRecognizer {
  constructor(onResult, onInterim) {
    this.onResult = onResult;     /* callback(finalText) */
    this.onInterim = onInterim;   /* callback(interimText) */
    this.recognition = null;
    this.active = false;
    this.supported = false;

    const SpeechAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechAPI) {
      console.warn('[SpeechRecognizer] Web Speech API not supported');
      return;
    }

    this.supported = true;
    this.recognition = new SpeechAPI();
    this.recognition.lang = 'fr-FR';
    this.recognition.interimResults = true;
    this.recognition.continuous = true;
    this.recognition.maxAlternatives = 1;

    this.recognition.onresult = (event) => {
      let interim = '';
      let finalText = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalText += transcript;
        } else {
          interim += transcript;
        }
      }

      if (interim && this.onInterim) this.onInterim(interim);
      if (finalText.trim()) this.onResult(finalText.trim());
    };

    this.recognition.onerror = (event) => {
      if (event.error !== 'no-speech') {
        console.error('[SpeechRecognizer] Error:', event.error);
      }
    };

    this.recognition.onend = () => {
      /* Restart automatically if still supposed to be active */
      if (this.active) {
        try { this.recognition.start(); } catch { /* already started */ }
      }
    };
  }

  start() {
    if (!this.supported) return false;
    this.active = true;
    try { this.recognition.start(); } catch { /* ignore if already running */ }
    return true;
  }

  stop() {
    this.active = false;
    if (this.recognition) this.recognition.stop();
  }

  toggle() {
    if (this.active) {
      this.stop();
      return false;
    } else {
      return this.start();
    }
  }
}

window.SpeechRecognizer = SpeechRecognizer;
