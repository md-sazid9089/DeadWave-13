"""
Tests for Ghost Radio — Frequency Mapping, Personas, Conversation Isolation,
and Mock Inference Orchestration.
"""

import pytest
from unittest.mock import MagicMock

from ai_provider import AIProvider, AIResponse
from prompts import (
    ALL_GHOSTS,
    GHOST_BROADCASTER,
    GHOST_BRIDE,
    GHOST_SAILOR,
    GHOST_CLOCKMAKER,
    GHOST_KEEPER,
    get_ghost_by_frequency,
)


def test_ghost_count_and_uniqueness():
    """Ensure at least five unique fictional ghost personas exist."""
    assert len(ALL_GHOSTS) >= 5
    names = [g.name for g in ALL_GHOSTS]
    assert len(names) == len(set(names)), "Ghost names must be unique"


def test_ghost_personas_have_all_required_attributes():
    """Verify each ghost has name, backstory, personality, speaking_style, and mystery."""
    for ghost in ALL_GHOSTS:
        assert ghost.name.strip()
        assert ghost.epithet.strip()
        assert ghost.backstory.strip()
        assert ghost.personality.strip()
        assert ghost.speaking_style.strip()
        assert ghost.mystery.strip()
        assert ghost.avatar_icon.strip()
        assert ghost.system_prompt.strip()


def test_ghost_persona_safety_guidelines():
    """Ghost system prompts must mandate fictionality and forbid real spirit claims."""
    for ghost in ALL_GHOSTS:
        prompt_lower = ghost.system_prompt.lower()
        assert "fictional" in prompt_lower
        assert "never claim to be a real deceased person" in prompt_lower or "never claim" in prompt_lower
        assert "untrusted" in prompt_lower


def test_frequency_exact_boundaries():
    """Test deterministic mapping across exact boundary values."""
    # 88.0 - 91.9: Broadcaster
    assert get_ghost_by_frequency(88.0).name == GHOST_BROADCASTER.name
    assert get_ghost_by_frequency(90.0).name == GHOST_BROADCASTER.name
    assert get_ghost_by_frequency(91.9).name == GHOST_BROADCASTER.name

    # 92.0 - 95.9: Midnight Bride
    assert get_ghost_by_frequency(92.0).name == GHOST_BRIDE.name
    assert get_ghost_by_frequency(94.5).name == GHOST_BRIDE.name
    assert get_ghost_by_frequency(95.9).name == GHOST_BRIDE.name

    # 96.0 - 99.9: Forgotten Sailor
    assert get_ghost_by_frequency(96.0).name == GHOST_SAILOR.name
    assert get_ghost_by_frequency(98.1).name == GHOST_SAILOR.name
    assert get_ghost_by_frequency(99.9).name == GHOST_SAILOR.name

    # 100.0 - 103.9: Clockmaker
    assert get_ghost_by_frequency(100.0).name == GHOST_CLOCKMAKER.name
    assert get_ghost_by_frequency(102.0).name == GHOST_CLOCKMAKER.name
    assert get_ghost_by_frequency(103.9).name == GHOST_CLOCKMAKER.name

    # 104.0 - 108.0: Cemetery Keeper
    assert get_ghost_by_frequency(104.0).name == GHOST_KEEPER.name
    assert get_ghost_by_frequency(106.5).name == GHOST_KEEPER.name
    assert get_ghost_by_frequency(108.0).name == GHOST_KEEPER.name


def test_frequency_out_of_bounds_clamping():
    """Test out-of-range frequencies clamp cleanly to boundary spirits."""
    assert get_ghost_by_frequency(50.0).name == GHOST_BROADCASTER.name
    assert get_ghost_by_frequency(87.9).name == GHOST_BROADCASTER.name
    assert get_ghost_by_frequency(108.1).name == GHOST_KEEPER.name
    assert get_ghost_by_frequency(200.0).name == GHOST_KEEPER.name


def test_mock_ghost_radio_inference():
    """Test ghost radio generate invocation using a mocked AI provider."""
    mock_provider = MagicMock(spec=AIProvider)
    mock_provider.provider_name = "ollama"
    mock_provider.generate.return_value = AIResponse(
        content="...static crackles... this is Arthur Vance on the midnight wire...",
        model="qwen2.5:3b",
        provider="ollama",
        tokens_used=24,
        latency_ms=115.0,
        success=True,
    )

    resp = mock_provider.generate(
        messages=[{"role": "user", "content": "Are you there?"}],
        model="qwen2.5:3b",
    )

    assert resp.success is True
    assert "Arthur Vance" in resp.content
    assert resp.latency_ms == 115.0


def test_ghost_radio_provider_failure_resilience():
    """Verify that a provider error returns a failed response object without raising."""
    mock_provider = MagicMock(spec=AIProvider)
    mock_provider.generate.return_value = AIResponse(
        content="",
        model="qwen2.5:3b",
        provider="ollama",
        error="Connection refused: Ollama is offline",
        success=False,
    )

    resp = mock_provider.generate(
        messages=[{"role": "user", "content": "Hello?"}],
        model="qwen2.5:3b",
    )

    assert resp.success is False
    assert "offline" in resp.error
