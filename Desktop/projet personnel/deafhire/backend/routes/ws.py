"""
WebSocket handler — real-time bidirectional communication
WS /ws/{session_id}/{role}

Messages:
  Candidate → sign_keypoints      → translate → broadcast sign_translation
  Recruiter → recruiter_message   → NLP       → broadcast recruiter_message
  Any       → ping                → pong
  Any       → webrtc_*            → forward to all other peers (P2P signaling)
"""

import time
import json
import logging
from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.sign_language import SignLanguageService
from services.nlp import NLPService
from database import add_transcript_entry

router = APIRouter(tags=["websocket"])
logger = logging.getLogger(__name__)

_sign_svc = SignLanguageService()
_nlp_svc  = NLPService()

_connections:   dict[str, list[WebSocket]] = defaultdict(list)
_session_start: dict[str, float]           = {}


@router.websocket("/ws/{session_id}/{role}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, role: str):
    await websocket.accept()
    _connections[session_id].append(websocket)
    if session_id not in _session_start:
        _session_start[session_id] = time.time()

    try:
        while True:
            raw      = await websocket.receive_text()
            msg      = json.loads(raw)
            msg_type = msg.get("type")
            payload  = msg.get("payload", {})

            # ── Ping / keep-alive ──────────────────────────────
            if msg_type == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": int(time.time() * 1000),
                })

            # ── Candidate: LSF sign → translation ─────────────
            elif msg_type == "sign_keypoints":
                result   = _sign_svc.translate(payload)
                time_sec = int(time.time() - _session_start.get(session_id, time.time()))

                if result.text:
                    _save_transcript(session_id, "candidate", result.text, time_sec)

                out = {
                    "type":       "sign_translation",
                    "session_id": session_id,
                    "timestamp":  int(time.time() * 1000),
                    "payload": {
                        "sign":       result.sign,
                        "text":       result.text,
                        "confidence": result.confidence,
                        "latency_ms": result.latency_ms,
                    },
                }
                await _broadcast(session_id, out, exclude=websocket)

            # ── Recruiter: text message → NLP → keywords ───────
            elif msg_type == "recruiter_message":
                text     = payload.get("text", "")
                nlp      = _nlp_svc.process_recruiter_message(text)
                time_sec = int(time.time() - _session_start.get(session_id, time.time()))

                _save_transcript(session_id, "recruiter", text, time_sec)

                out = {
                    "type":       "recruiter_message",
                    "session_id": session_id,
                    "timestamp":  int(time.time() * 1000),
                    "payload": {
                        "text":           nlp.original,
                        "simplified_text": nlp.simplified,
                        "sign_keywords":  nlp.sign_keywords,
                    },
                }
                await _broadcast(session_id, out, exclude=websocket)

            # ── WebRTC P2P signaling — pure relay ─────────────
            elif msg_type in ("webrtc_ready", "webrtc_offer", "webrtc_answer", "webrtc_ice"):
                await _broadcast(session_id, {
                    "type":       msg_type,
                    "session_id": session_id,
                    "payload":    payload,
                }, exclude=websocket)

    except WebSocketDisconnect:
        _connections[session_id].remove(websocket)
        if not _connections[session_id]:
            del _connections[session_id]
            _session_start.pop(session_id, None)


# ── Helpers ───────────────────────────────────────────────

async def _broadcast(session_id: str, data: dict, exclude: Optional[WebSocket] = None):
    dead = []
    for ws in list(_connections.get(session_id, [])):
        if ws is exclude:
            continue
        try:
            await ws.send_json(data)
        except Exception:
            dead.append(ws)
    for ws in dead:
        try:
            _connections[session_id].remove(ws)
        except ValueError:
            pass


def _save_transcript(session_id: str, role: str, text: str, time_sec: int):
    try:
        add_transcript_entry(session_id, role, text, time_sec)
    except Exception as exc:
        logger.debug(f"[WS] Transcript save skipped: {exc}")
