from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class Role(str, Enum):
    recruiter = "recruiter"
    candidate = "candidate"


class InterviewStatus(str, Enum):
    pending   = "pending"
    active    = "active"
    completed = "completed"
    rejected  = "rejected"


# ── Session ──────────────────────────────────────────────

class SessionCreate(BaseModel):
    candidate_name:  str            = Field(..., min_length=2, max_length=100)
    candidate_role:  str            = Field(..., min_length=2, max_length=100)
    candidate_email: Optional[str]  = None
    scheduled_at:    Optional[datetime] = None
    lsf_enabled:     bool           = True


class SessionResponse(BaseModel):
    session_id:          str
    candidate_name:      str
    candidate_role:      str
    status:              str
    created_at:          datetime
    join_url_candidate:  str
    join_url_recruiter:  str
    notes:               Optional[str] = None
    decision:            Optional[str] = None


class SessionUpdate(BaseModel):
    status:    Optional[str] = Field(None, pattern=r'^(pending|active|completed|rejected)$')
    notes:     Optional[str] = Field(None, max_length=4000)
    decision:  Optional[str] = Field(None, pattern=r'^(retained|pending|rejected)$')
    ended_at:  Optional[str] = None


# ── Translation ───────────────────────────────────────────

class KeypointPayload(BaseModel):
    keypoints: dict
    timestamp: int


class TranslationResult(BaseModel):
    sign:        str
    text:        str
    confidence:  float
    latency_ms:  int


class RecruiterMessage(BaseModel):
    text:             str
    simplified_text:  str
    sign_keywords:    list[str]


# ── WebSocket messages ────────────────────────────────────

class WSIncoming(BaseModel):
    type:    str   # "sign_keypoints" | "recruiter_message" | "ping"
    payload: dict


class WSOutgoing(BaseModel):
    type:       str
    payload:    dict
    session_id: str
    timestamp:  int


# ── Transcript ────────────────────────────────────────────

class TranscriptEntry(BaseModel):
    role:       str
    text:       str
    time_sec:   int
    created_at: Optional[str] = None


class TranscriptResponse(BaseModel):
    session_id:       str
    entries:          list[TranscriptEntry]
    duration_seconds: int
