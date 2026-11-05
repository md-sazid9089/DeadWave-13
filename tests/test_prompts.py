"""Tests for prompts module."""

import pytest


def test_ghost_radio_system_prompt():
    """Ghost Radio system prompt should be defined and non-empty."""
    from prompts import GHOST_RADIO_SYSTEM
    assert len(GHOST_RADIO_SYSTEM) > 100
    assert "DeadWave" in GHOST_RADIO_SYSTEM


def test_ghost_radio_user_template():
    """Ghost Radio user template should format correctly."""
    from prompts import GHOST_RADIO_USER_TEMPLATE
    formatted = GHOST_RADIO_USER_TEMPLATE.format(
        frequency=6.66,
        signal_strength="STRONG 🟢",
        user_input="Is anyone there?",
    )
    assert "6.66" in formatted
    assert "Is anyone there?" in formatted


def test_curse_decoder_system_prompt():
    """Curse Decoder system prompt should be defined and non-empty."""
    from prompts import CURSE_DECODER_SYSTEM
    assert len(CURSE_DECODER_SYSTEM) > 100
    assert "Curse" in CURSE_DECODER_SYSTEM


def test_curse_decoder_user_template():
    """Curse Decoder user template should format correctly."""
    from prompts import CURSE_DECODER_USER_TEMPLATE
    formatted = CURSE_DECODER_USER_TEMPLATE.format(
        user_input="My mirrors are haunted"
    )
    assert "My mirrors are haunted" in formatted
