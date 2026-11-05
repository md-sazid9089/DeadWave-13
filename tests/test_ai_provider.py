"""Tests for AI provider module."""

import pytest
from unittest.mock import patch, MagicMock


def test_ai_response_model():
    """AIResponse should construct properly."""
    from ai_provider import AIResponse

    resp = AIResponse(
        content="Hello from beyond",
        model="qwen2.5:3b",
        provider="ollama",
        tokens_used=42,
        latency_ms=123.4,
    )
    assert resp.success is True
    assert resp.error is None
    assert resp.content == "Hello from beyond"


def test_ai_response_error():
    """AIResponse should handle error states."""
    from ai_provider import AIResponse

    resp = AIResponse(
        content="",
        model="qwen2.5:3b",
        provider="ollama",
        error="Connection refused",
        success=False,
    )
    assert resp.success is False
    assert "Connection" in resp.error


def test_model_info():
    """ModelInfo should construct properly."""
    from ai_provider import ModelInfo

    info = ModelInfo(name="qwen2.5:3b", provider="ollama", available=True)
    assert info.name == "qwen2.5:3b"
    assert info.available is True


def test_ollama_provider_properties():
    """OllamaProvider should have correct properties."""
    from ai_provider import OllamaProvider

    provider = OllamaProvider()
    assert provider.provider_name == "ollama"
    assert provider.is_cloud is False


def test_ollama_check_availability_offline():
    """OllamaProvider should handle offline gracefully."""
    from ai_provider import OllamaProvider

    provider = OllamaProvider(base_url="http://localhost:99999")
    assert provider.check_availability() is False


def test_context_bounding():
    """Context bounding should preserve system messages and trim old messages."""
    from ai_provider import OllamaProvider
    import config

    provider = OllamaProvider()
    original_max = config.MAX_CONTEXT_MESSAGES
    config.MAX_CONTEXT_MESSAGES = 5

    try:
        messages = [
            {"role": "system", "content": "System prompt"},
            *[{"role": "user", "content": f"msg {i}"} for i in range(10)],
        ]
        bounded = provider._bound_context(messages)

        # System message should always be present
        assert bounded[0]["role"] == "system"
        # Total should be <= MAX_CONTEXT_MESSAGES
        assert len(bounded) <= config.MAX_CONTEXT_MESSAGES + 1  # +1 for system
        # Most recent messages should be kept
        assert bounded[-1]["content"] == "msg 9"
    finally:
        config.MAX_CONTEXT_MESSAGES = original_max


def test_get_provider_ollama():
    """get_provider should return OllamaProvider for 'ollama'."""
    from ai_provider import get_provider, OllamaProvider

    provider = get_provider("ollama")
    assert isinstance(provider, OllamaProvider)


def test_get_provider_invalid():
    """get_provider should raise for unknown provider."""
    from ai_provider import get_provider

    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider("nonexistent")


def test_get_provider_grok_no_key():
    """get_provider should raise for grok without API key."""
    from ai_provider import get_provider
    import config

    original = config.GROK_AVAILABLE
    config.GROK_AVAILABLE = False
    try:
        with pytest.raises(ValueError, match="XAI_API_KEY"):
            get_provider("grok")
    finally:
        config.GROK_AVAILABLE = original


def test_ollama_generate_connection_error():
    """OllamaProvider.generate should handle connection errors gracefully."""
    from ai_provider import OllamaProvider

    provider = OllamaProvider(base_url="http://localhost:99999")
    response = provider.generate(
        messages=[{"role": "user", "content": "hello"}],
        model="qwen2.5:3b",
    )
    assert response.success is False
    assert response.error is not None
    assert response.provider == "ollama"
