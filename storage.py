"""
DeadWave 13 — SQLite Storage Layer
Handles database initialization, session logging, message persistence,
and curse case records with WAL mode and transaction safety.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator

from config import DB_PATH

logger = logging.getLogger(__name__)

# ── Schema ────────────────────────────────────────────────────────────────────
_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT    NOT NULL UNIQUE,
    feature     TEXT    NOT NULL,          -- 'ghost_radio' | 'curse_decoder'
    provider    TEXT    NOT NULL,          -- 'ollama' | 'grok'
    model       TEXT    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT    NOT NULL,
    role        TEXT    NOT NULL,          -- 'user' | 'assistant' | 'system'
    content     TEXT    NOT NULL,
    metadata    TEXT,                      -- JSON blob for extra data
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

CREATE TABLE IF NOT EXISTS curse_cases (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id        TEXT    NOT NULL UNIQUE,
    haunted_object TEXT    NOT NULL,
    case_title     TEXT    NOT NULL,
    status         TEXT    NOT NULL,       -- 'active', 'solved', 'failed'
    attempts_used  INTEGER NOT NULL DEFAULT 0,
    case_data      TEXT    NOT NULL,       -- JSON blob with puzzle schema
    created_at     TEXT    NOT NULL DEFAULT (datetime('now')),
    completed_at   TEXT
);

CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_feature ON sessions(feature);
CREATE INDEX IF NOT EXISTS idx_curse_cases_created ON curse_cases(created_at DESC);
"""


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for SQLite connections with WAL mode."""
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Initialize the database schema. Safe to call multiple times."""
    try:
        with get_connection() as conn:
            conn.executescript(_SCHEMA)
        logger.info("Database initialized at %s", DB_PATH)
    except sqlite3.Error as e:
        logger.error("Failed to initialize database: %s", e)
        raise


def create_session(
    session_id: str,
    feature: str,
    provider: str,
    model: str,
) -> None:
    """Create a new session record or ignore if exists."""
    with get_connection() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO sessions (session_id, feature, provider, model)
               VALUES (?, ?, ?, ?)""",
            (session_id, feature, provider, model),
        )


def save_message(
    session_id: str,
    role: str,
    content: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Persist a message to the database."""
    meta_json = json.dumps(metadata) if metadata else None
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO messages (session_id, role, content, metadata)
               VALUES (?, ?, ?, ?)""",
            (session_id, role, content, meta_json),
        )
        conn.execute(
            """UPDATE sessions SET updated_at = ? WHERE session_id = ?""",
            (datetime.now(timezone.utc).isoformat(), session_id),
        )


def get_messages(session_id: str, limit: int | None = None) -> list[dict[str, Any]]:
    """Retrieve messages for a session, optionally limited."""
    with get_connection() as conn:
        query = """SELECT role, content, metadata, created_at
                   FROM messages WHERE session_id = ?
                   ORDER BY id ASC"""
        if limit:
            query += f" LIMIT {int(limit)}"
        rows = conn.execute(query, (session_id,)).fetchall()
        return [
            {
                "role": row["role"],
                "content": row["content"],
                "metadata": json.loads(row["metadata"]) if row["metadata"] else None,
                "created_at": row["created_at"],
            }
            for row in rows
        ]


def clear_session_messages(session_id: str) -> None:
    """Remove all messages for a specific session."""
    with get_connection() as conn:
        conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))


def get_recent_sessions(feature: str, limit: int = 10) -> list[dict[str, Any]]:
    """Get recent sessions for a feature."""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT session_id, provider, model, created_at, updated_at
               FROM sessions WHERE feature = ?
               ORDER BY updated_at DESC LIMIT ?""",
            (feature, limit),
        ).fetchall()
        return [dict(row) for row in rows]


def save_curse_case(
    case_id: str,
    haunted_object: str,
    case_title: str,
    status: str,
    attempts_used: int,
    case_data: dict[str, Any],
) -> None:
    """Save or update a curse case record."""
    data_json = json.dumps(case_data)
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO curse_cases (case_id, haunted_object, case_title, status, attempts_used, case_data)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(case_id) DO UPDATE SET
                   status = excluded.status,
                   attempts_used = excluded.attempts_used,
                   case_data = excluded.case_data""",
            (case_id, haunted_object, case_title, status, attempts_used, data_json),
        )


def update_curse_status(
    case_id: str,
    status: str,
    attempts_used: int,
) -> None:
    """Update status of a completed or failed curse case."""
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            """UPDATE curse_cases
               SET status = ?, attempts_used = ?, completed_at = ?
               WHERE case_id = ?""",
            (status, attempts_used, now_iso, case_id),
        )


def get_recent_curse_cases(limit: int = 6) -> list[dict[str, Any]]:
    """Retrieve recently logged curse cases."""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT case_id, haunted_object, case_title, status, attempts_used, created_at, completed_at
               FROM curse_cases
               ORDER BY id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_recent_transmissions(limit: int = 6) -> list[dict[str, Any]]:
    """Retrieve recent Ghost Radio transmissions with spirit info."""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT m.content, m.metadata, m.created_at, s.provider, s.model
               FROM messages m
               JOIN sessions s ON m.session_id = s.session_id
               WHERE s.feature = 'ghost_radio' AND m.role = 'assistant'
               ORDER BY m.id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        results = []
        for row in rows:
            meta = json.loads(row["metadata"]) if row["metadata"] else {}
            results.append({
                "content": row["content"],
                "frequency": meta.get("frequency", "Unknown"),
                "ghost_name": meta.get("ghost_name", "Unknown Spirit"),
                "latency_ms": meta.get("latency_ms", 0),
                "created_at": row["created_at"],
                "provider": row["provider"],
                "model": row["model"],
            })
        return results
