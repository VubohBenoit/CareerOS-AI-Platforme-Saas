"""
SQLite Database — DeafHire
Persistent storage for sessions, users, and transcripts.
Uses a simple sqlite3 wrapper (no ORM overhead for a prototype).
"""

import sqlite3
import threading
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "deafhire.db"

# Thread-local connections for safety
_local = threading.local()


def get_conn() -> sqlite3.Connection:
    if not hasattr(_local, "conn") or _local.conn is None:
        _local.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA journal_mode=WAL")
        _local.conn.execute("PRAGMA foreign_keys=ON")
    return _local.conn


def init_db():
    """Create tables if they don't exist. Called at app startup."""
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            email       TEXT    UNIQUE NOT NULL,
            name        TEXT    NOT NULL,
            company     TEXT    NOT NULL DEFAULT '',
            password_hash TEXT  NOT NULL,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      TEXT    UNIQUE NOT NULL,
            candidate_name  TEXT    NOT NULL,
            candidate_role  TEXT    NOT NULL,
            candidate_email TEXT,
            lsf_enabled     INTEGER NOT NULL DEFAULT 1,
            status          TEXT    NOT NULL DEFAULT 'pending',
            created_by      TEXT,
            scheduled_at    TEXT,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
            ended_at        TEXT,
            notes           TEXT,
            decision        TEXT
        );

        CREATE TABLE IF NOT EXISTS transcript_entries (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT    NOT NULL,
            role        TEXT    NOT NULL,
            text        TEXT    NOT NULL,
            time_sec    INTEGER NOT NULL DEFAULT 0,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        );

        CREATE INDEX IF NOT EXISTS idx_sessions_sid    ON sessions(session_id);
        CREATE INDEX IF NOT EXISTS idx_transcript_sid  ON transcript_entries(session_id);
    """)
    conn.commit()

    # Seed default admin if not present
    _seed_admin(conn)


def add_transcript_entry(session_id: str, role: str, text: str, time_sec: int) -> None:
    conn = get_conn()
    conn.execute(
        "INSERT INTO transcript_entries (session_id, role, text, time_sec) VALUES (?,?,?,?)",
        (session_id, role, text, time_sec),
    )
    conn.commit()


def _seed_admin(conn: sqlite3.Connection):
    from services.auth import hash_password
    exists = conn.execute("SELECT 1 FROM users WHERE email=?", ("admin@deafhire.fr",)).fetchone()
    if not exists:
        conn.execute(
            "INSERT INTO users (email, name, company, password_hash) VALUES (?,?,?,?)",
            ("admin@deafhire.fr", "Admin DeafHire", "DeafHire", hash_password("deafhire2026"))
        )
        conn.commit()
