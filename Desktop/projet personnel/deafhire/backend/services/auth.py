"""
Authentication Service
- Password hashing with bcrypt
- JWT token creation and verification
"""

import hashlib
import hmac
import base64
import json
import time
from datetime import datetime, timedelta
from typing import Optional

from core.config import get_settings

settings = get_settings()


# ── Password hashing (bcrypt-like with sha256 for simplicity) ──

def hash_password(password: str) -> str:
    """Returns a salted sha256 hash prefixed with algorithm tag."""
    import secrets
    salt = secrets.token_hex(16)
    h = hashlib.sha256(f"{salt}{password}{settings.SECRET_KEY}".encode()).hexdigest()
    return f"sha256${salt}${h}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored hash."""
    try:
        algo, salt, h = stored_hash.split("$")
        expected = hashlib.sha256(f"{salt}{password}{settings.SECRET_KEY}".encode()).hexdigest()
        return hmac.compare_digest(expected, h)
    except Exception:
        return False


# ── JWT (minimal, no external lib) ──

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    pad = 4 - len(s) % 4
    return base64.urlsafe_b64decode(s + "=" * pad)


def create_token(user_data: dict, expire_hours: int = 24) -> str:
    header  = _b64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = {
        **user_data,
        "iat": int(time.time()),
        "exp": int(time.time()) + expire_hours * 3600,
    }
    body = _b64url(json.dumps(payload).encode())
    sig_input = f"{header}.{body}".encode()
    sig = hmac.new(settings.SECRET_KEY.encode(), sig_input, hashlib.sha256).digest()
    return f"{header}.{body}.{_b64url(sig)}"


def verify_token(token: str) -> Optional[dict]:
    try:
        header, body, sig = token.split(".")
        sig_input = f"{header}.{body}".encode()
        expected_sig = hmac.new(settings.SECRET_KEY.encode(), sig_input, hashlib.sha256).digest()
        actual_sig = _b64url_decode(sig)
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        payload = json.loads(_b64url_decode(body))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


# ── DB helpers ──

def get_user_by_email(email: str) -> Optional[dict]:
    from database import get_conn
    row = get_conn().execute(
        "SELECT * FROM users WHERE email=?", (email,)
    ).fetchone()
    return dict(row) if row else None


def create_user(email: str, name: str, company: str, password: str) -> Optional[dict]:
    from database import get_conn
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO users (email, name, company, password_hash) VALUES (?,?,?,?)",
            (email, name, company, hash_password(password))
        )
        conn.commit()
        return get_user_by_email(email)
    except Exception:
        return None
