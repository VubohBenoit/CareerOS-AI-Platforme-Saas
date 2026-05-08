"""
Session management routes — backed by SQLite
POST /sessions                   → create session + send email invitation
GET  /sessions                   → list sessions for current recruiter (filtered)
GET  /sessions/validate/{id}     → public session check (no auth)
GET  /sessions/{id}              → get session details
PATCH /sessions/{id}             → update status/notes/decision (owner only)
GET  /sessions/{id}/transcript   → download transcript
"""

import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from models.schemas import SessionCreate, SessionResponse, SessionUpdate, TranscriptResponse
from services.auth import verify_token
from services.email import send_interview_invitation
from database import get_conn

router   = APIRouter(prefix="/sessions", tags=["sessions"])
security = HTTPBearer(auto_error=False)


def _current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[dict]:
    if not credentials:
        return None
    return verify_token(credentials.credentials)


def _require_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    if not credentials:
        raise HTTPException(401, "Authentification requise")
    user = verify_token(credentials.credentials)
    if not user:
        raise HTTPException(401, "Token invalide ou expiré")
    return user


# ── Create session ───────────────────────────────────────────

@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(body: SessionCreate, request: Request,
                         user: dict = Depends(_current_user)):
    session_id = str(uuid.uuid4())[:8].upper()
    base_url   = str(request.base_url).rstrip("/")
    now        = datetime.utcnow().isoformat()
    created_by = user["sub"] if user else "anonymous"

    conn = get_conn()
    conn.execute(
        """INSERT INTO sessions
           (session_id, candidate_name, candidate_role, candidate_email,
            lsf_enabled, status, created_by, scheduled_at, created_at)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (session_id, body.candidate_name, body.candidate_role,
         body.candidate_email, int(body.lsf_enabled), "pending",
         created_by, body.scheduled_at.isoformat() if body.scheduled_at else None, now),
    )
    conn.commit()

    join_url = f"{base_url}/join.html?session={session_id}"

    if body.candidate_email:
        send_interview_invitation(
            to_email       = body.candidate_email,
            candidate_name = body.candidate_name,
            session_id     = session_id,
            scheduled_at   = body.scheduled_at,
            join_url       = join_url,
        )

    return SessionResponse(
        session_id         = session_id,
        candidate_name     = body.candidate_name,
        candidate_role     = body.candidate_role,
        status             = "pending",
        created_at         = datetime.fromisoformat(now),
        join_url_candidate = join_url,
        join_url_recruiter = f"{base_url}/interview.html?role=recruiter&session={session_id}",
    )


# ── List sessions (filtered by owner) ───────────────────────

@router.get("")
async def list_sessions(user: dict = Depends(_current_user)):
    conn = get_conn()
    if user:
        rows = conn.execute(
            "SELECT * FROM sessions WHERE created_by=? ORDER BY created_at DESC LIMIT 100",
            (user["sub"],),
        ).fetchall()
    else:
        # Demo mode: return all (no auth), limited to 50
        rows = conn.execute(
            "SELECT * FROM sessions ORDER BY created_at DESC LIMIT 50"
        ).fetchall()
    return [dict(r) for r in rows]


# ── Validate session — public, no auth ──────────────────────
# MUST be declared before /{session_id} to avoid route shadowing

@router.get("/validate/{session_id}")
async def validate_session(session_id: str):
    conn = get_conn()
    row  = conn.execute(
        "SELECT session_id, candidate_name, candidate_role, status FROM sessions WHERE session_id=?",
        (session_id,),
    ).fetchone()
    if not row:
        raise HTTPException(404, "Session introuvable")
    s = dict(row)
    return {
        "valid":          True,
        "session_id":     s["session_id"],
        "candidate_name": s["candidate_name"],
        "candidate_role": s["candidate_role"],
        "status":         s["status"],
    }


# ── Get one session ──────────────────────────────────────────

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, request: Request):
    conn = get_conn()
    row  = conn.execute(
        "SELECT * FROM sessions WHERE session_id=?", (session_id,)
    ).fetchone()
    if not row:
        raise HTTPException(404, "Session introuvable")

    base_url = str(request.base_url).rstrip("/")
    s = dict(row)
    return SessionResponse(
        session_id         = s["session_id"],
        candidate_name     = s["candidate_name"],
        candidate_role     = s["candidate_role"],
        status             = s["status"],
        created_at         = datetime.fromisoformat(s["created_at"]),
        join_url_candidate = f"{base_url}/join.html?session={session_id}",
        join_url_recruiter = f"{base_url}/interview.html?role=recruiter&session={session_id}",
        notes              = s.get("notes"),
        decision           = s.get("decision"),
    )


# ── Update session (owner only) ──────────────────────────────

@router.patch("/{session_id}")
async def update_session(session_id: str, body: SessionUpdate,
                         user: dict = Depends(_current_user)):
    conn = get_conn()
    row  = conn.execute(
        "SELECT created_by FROM sessions WHERE session_id=?", (session_id,)
    ).fetchone()
    if not row:
        raise HTTPException(404, "Session introuvable")

    # Ownership check — bypass only in demo mode (no auth)
    if user and row["created_by"] not in (user["sub"], "anonymous"):
        raise HTTPException(403, "Accès refusé")

    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        return {"ok": True}

    set_clause = ", ".join(f"{k}=?" for k in updates)
    conn.execute(
        f"UPDATE sessions SET {set_clause} WHERE session_id=?",
        (*updates.values(), session_id),
    )
    conn.commit()
    return {"ok": True}


# ── Transcript ────────────────────────────────────────────────

@router.get("/{session_id}/transcript", response_model=TranscriptResponse)
async def get_transcript(session_id: str):
    conn = get_conn()
    if not conn.execute("SELECT 1 FROM sessions WHERE session_id=?", (session_id,)).fetchone():
        raise HTTPException(404, "Session introuvable")

    rows = conn.execute(
        "SELECT role, text, time_sec, created_at FROM transcript_entries WHERE session_id=? ORDER BY time_sec",
        (session_id,),
    ).fetchall()

    entries  = [dict(r) for r in rows]
    duration = entries[-1]["time_sec"] if entries else 0
    return TranscriptResponse(session_id=session_id, entries=entries, duration_seconds=duration)
