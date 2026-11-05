"""Tests for storage module."""

import os
import pytest
import sqlite3
from pathlib import Path


@pytest.fixture(autouse=True)
def _use_temp_db(tmp_path, monkeypatch):
    """Redirect DB_PATH to a temp directory for testing."""
    test_db = tmp_path / "test_deadwave.db"
    monkeypatch.setattr("config.DB_PATH", test_db)
    # Also patch the storage module's reference
    import storage
    monkeypatch.setattr(storage, "DB_PATH", test_db)


def test_init_db():
    """Database should initialize without errors."""
    from storage import init_db, get_connection
    init_db()

    with get_connection() as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = {row["name"] for row in tables}
        assert "sessions" in table_names
        assert "messages" in table_names


def test_init_db_idempotent():
    """Calling init_db multiple times should be safe."""
    from storage import init_db
    init_db()
    init_db()  # Should not raise


def test_create_session():
    """Should create a session record."""
    from storage import init_db, create_session, get_connection

    init_db()
    create_session("test-sess-1", "ghost_radio", "ollama", "qwen2.5:3b")

    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?", ("test-sess-1",)
        ).fetchone()
        assert row is not None
        assert row["feature"] == "ghost_radio"
        assert row["provider"] == "ollama"


def test_save_and_get_messages():
    """Should save and retrieve messages."""
    from storage import init_db, create_session, save_message, get_messages

    init_db()
    create_session("test-sess-2", "curse_decoder", "ollama", "qwen2.5:3b")
    save_message("test-sess-2", "user", "I see shadows")
    save_message("test-sess-2", "assistant", "Curse detected!", {"severity": 7})

    messages = get_messages("test-sess-2")
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "I see shadows"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["metadata"]["severity"] == 7


def test_get_messages_with_limit():
    """Should respect the limit parameter."""
    from storage import init_db, create_session, save_message, get_messages

    init_db()
    create_session("test-sess-3", "ghost_radio", "ollama", "qwen2.5:3b")
    for i in range(5):
        save_message("test-sess-3", "user", f"Message {i}")

    messages = get_messages("test-sess-3", limit=3)
    assert len(messages) == 3


def test_get_recent_sessions():
    """Should retrieve recent sessions for a feature."""
    from storage import init_db, create_session, get_recent_sessions

    init_db()
    create_session("sess-a", "ghost_radio", "ollama", "qwen2.5:3b")
    create_session("sess-b", "ghost_radio", "grok", "grok-3-mini")
    create_session("sess-c", "curse_decoder", "ollama", "qwen2.5:3b")

    radio_sessions = get_recent_sessions("ghost_radio")
    assert len(radio_sessions) == 2

    decoder_sessions = get_recent_sessions("curse_decoder")
    assert len(decoder_sessions) == 1
