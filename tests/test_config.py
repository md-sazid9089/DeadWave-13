"""Tests for config module."""

import os
import pytest


def test_config_loads():
    """Config module should load without errors."""
    import config
    assert config.APP_NAME == "DeadWave 13"
    assert config.APP_VERSION == "0.1.0"


def test_config_defaults():
    """Config should have sensible defaults."""
    import config
    assert config.DEFAULT_PROVIDER in ("ollama", "grok")
    assert config.OLLAMA_BASE_URL.startswith("http")
    assert config.AI_TIMEOUT > 0
    assert config.MAX_CONTEXT_MESSAGES > 0
    assert config.MAX_TOKENS > 0
    assert 0.0 <= config.TEMPERATURE <= 2.0


def test_ollama_models_list():
    """Config should have Ollama models defined."""
    import config
    assert len(config.OLLAMA_MODELS) >= 3
    assert "qwen2.5:3b" in config.OLLAMA_MODELS


def test_grok_availability_flag():
    """GROK_AVAILABLE should reflect XAI_API_KEY presence."""
    import config
    if os.getenv("XAI_API_KEY"):
        assert config.GROK_AVAILABLE is True
    else:
        assert config.GROK_AVAILABLE is False
