"""
DeadWave 13 — AI Provider Abstraction
Unified interface for Ollama (local open-weight AI) and Grok/xAI (cloud) inference.
Supports runtime provider switching, model availability checks, bounded context,
and structured JSON generation for curse puzzles.
"""

from __future__ import annotations

import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Any

import requests
from pydantic import BaseModel, Field

import config

logger = logging.getLogger(__name__)


# ── Response Models ───────────────────────────────────────────────────────────
class AIResponse(BaseModel):
    """Structured response from any AI provider."""
    content: str
    model: str
    provider: str
    tokens_used: int | None = None
    latency_ms: float = 0.0
    error: str | None = None
    success: bool = True


class ModelInfo(BaseModel):
    """Information about an available model."""
    name: str
    provider: str
    size: str | None = None
    available: bool = True


# ── Abstract Provider ─────────────────────────────────────────────────────────
class AIProvider(ABC):
    """Base class for AI inference providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider identifier ('ollama' or 'grok')."""
        ...

    @property
    @abstractmethod
    def is_cloud(self) -> bool:
        """Whether this provider makes external API calls."""
        ...

    @abstractmethod
    def check_availability(self) -> bool:
        """Check if the provider is reachable and operational."""
        ...

    @abstractmethod
    def list_models(self) -> list[ModelInfo]:
        """List available models for this provider."""
        ...

    @abstractmethod
    def generate(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: str | dict[str, Any] | None = None,
    ) -> AIResponse:
        """Generate a response from the given message history."""
        ...

    def _bound_context(
        self, messages: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        """Trim message history to MAX_CONTEXT_MESSAGES, preserving all system messages."""
        system_msgs = [m for m in messages if m.get("role") == "system"]
        other_msgs = [m for m in messages if m.get("role") != "system"]

        max_other = max(1, config.MAX_CONTEXT_MESSAGES - len(system_msgs))
        if len(other_msgs) > max_other:
            other_msgs = other_msgs[-max_other:]

        return system_msgs + other_msgs


# ── Ollama Provider ──────────────────────────────────────────────────────────
class OllamaProvider(AIProvider):
    """Local offline inference via Ollama."""

    def __init__(self, base_url: str | None = None):
        self._base_url = (base_url or config.OLLAMA_BASE_URL).rstrip("/")
        self._timeout = config.AI_TIMEOUT

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def is_cloud(self) -> bool:
        return False

    def check_availability(self) -> bool:
        """Ping the local Ollama server tags endpoint quickly."""
        try:
            resp = requests.get(f"{self._base_url}/api/tags", timeout=1.5)
            return resp.status_code == 200
        except requests.ConnectionError:
            logger.debug("Ollama server not reachable at %s", self._base_url)
            return False
        except Exception as e:
            logger.debug("Ollama availability check failed: %s", e)
            return False

    def list_models(self) -> list[ModelInfo]:
        """List models available in the local Ollama instance."""
        if not self.check_availability():
            return [
                ModelInfo(name=m, provider="ollama", available=False)
                for m in config.OLLAMA_MODELS
            ]
        try:
            resp = requests.get(f"{self._base_url}/api/tags", timeout=2.0)
            resp.raise_for_status()
            data = resp.json()
            raw_models = data.get("models", [])
            installed_names = {m.get("name", "") for m in raw_models}

            models = []
            for model_name in config.OLLAMA_MODELS:
                is_available = (
                    model_name in installed_names
                    or any(model_name in inst for inst in installed_names)
                    or any(inst.startswith(model_name.split(":")[0]) for inst in installed_names)
                )
                models.append(
                    ModelInfo(
                        name=model_name,
                        provider="ollama",
                        available=is_available,
                    )
                )
            return models
        except Exception as e:
            logger.warning("Failed to list Ollama models: %s", e)
            return [
                ModelInfo(name=m, provider="ollama", available=False)
                for m in config.OLLAMA_MODELS
            ]

    def generate(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: str | dict[str, Any] | None = None,
    ) -> AIResponse:
        """Generate a response using Ollama's chat API."""
        model = model or config.OLLAMA_DEFAULT_MODEL
        temperature = temperature if temperature is not None else config.TEMPERATURE
        max_tokens = max_tokens or config.MAX_TOKENS
        bounded = self._bound_context(messages)

        payload: dict[str, Any] = {
            "model": model,
            "messages": bounded,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        # Add structured output format if requested
        if response_format:
            payload["format"] = response_format

        start = time.perf_counter()
        try:
            resp = requests.post(
                f"{self._base_url}/api/chat",
                json=payload,
                timeout=self._timeout,
            )
            elapsed = (time.perf_counter() - start) * 1000

            if resp.status_code == 404:
                return AIResponse(
                    content="",
                    model=model,
                    provider="ollama",
                    latency_ms=round(elapsed, 1),
                    error=f"Model '{model}' not found in Ollama. Pull it with: `ollama pull {model}`",
                    success=False,
                )

            resp.raise_for_status()
            data = resp.json()

            content = data.get("message", {}).get("content", "")
            eval_count = data.get("eval_count")

            return AIResponse(
                content=content,
                model=model,
                provider="ollama",
                tokens_used=eval_count,
                latency_ms=round(elapsed, 1),
            )

        except requests.ConnectionError:
            elapsed = (time.perf_counter() - start) * 1000
            return AIResponse(
                content="",
                model=model,
                provider="ollama",
                latency_ms=round(elapsed, 1),
                error="Ollama server is not running locally. Start it with: `ollama serve`",
                success=False,
            )
        except requests.Timeout:
            elapsed = (time.perf_counter() - start) * 1000
            return AIResponse(
                content="",
                model=model,
                provider="ollama",
                latency_ms=round(elapsed, 1),
                error=f"Ollama request timed out after {self._timeout}s",
                success=False,
            )
        except requests.HTTPError as e:
            elapsed = (time.perf_counter() - start) * 1000
            error_detail = ""
            try:
                error_detail = e.response.json().get("error", str(e))
            except Exception:
                error_detail = str(e)
            return AIResponse(
                content="",
                model=model,
                provider="ollama",
                latency_ms=round(elapsed, 1),
                error=f"Ollama HTTP error: {error_detail}",
                success=False,
            )
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            logger.exception("Unexpected error during Ollama inference")
            return AIResponse(
                content="",
                model=model,
                provider="ollama",
                latency_ms=round(elapsed, 1),
                error=f"Unexpected error: {e}",
                success=False,
            )


# ── Grok Provider ────────────────────────────────────────────────────────────
class GrokProvider(AIProvider):
    """Cloud inference via xAI's Grok API (OpenAI-compatible SDK)."""

    def __init__(self):
        if not config.GROK_AVAILABLE:
            raise ValueError(
                "XAI_API_KEY not set. Cannot initialize Grok provider."
            )
        from openai import OpenAI
        self._client = OpenAI(
            api_key=config.XAI_API_KEY,
            base_url=config.GROK_BASE_URL,
            timeout=config.AI_TIMEOUT,
        )
        self._timeout = config.AI_TIMEOUT

    @property
    def provider_name(self) -> str:
        return "grok"

    @property
    def is_cloud(self) -> bool:
        return True

    def check_availability(self) -> bool:
        """Check if the Grok API is reachable with the provided key."""
        try:
            self._client.models.list()
            return True
        except Exception as e:
            logger.warning("Grok API availability check failed: %s", e)
            return False

    def list_models(self) -> list[ModelInfo]:
        """Return the configured Grok model."""
        return [
            ModelInfo(
                name=config.GROK_MODEL,
                provider="grok",
                available=self.check_availability(),
            )
        ]

    def generate(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: str | dict[str, Any] | None = None,
    ) -> AIResponse:
        """Generate a response using the Grok API."""
        model = model or config.GROK_MODEL
        temperature = temperature if temperature is not None else config.TEMPERATURE
        max_tokens = max_tokens or config.MAX_TOKENS
        bounded = self._bound_context(messages)

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": bounded,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format:
            if response_format == "json":
                kwargs["response_format"] = {"type": "json_object"}
            elif isinstance(response_format, dict):
                kwargs["response_format"] = response_format

        start = time.perf_counter()
        try:
            response = self._client.chat.completions.create(**kwargs)
            elapsed = (time.perf_counter() - start) * 1000

            content = response.choices[0].message.content or ""
            tokens = (
                response.usage.total_tokens if response.usage else None
            )

            return AIResponse(
                content=content,
                model=model,
                provider="grok",
                tokens_used=tokens,
                latency_ms=round(elapsed, 1),
            )

        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            # Sanitize error message to prevent secret leaking
            err_msg = str(e)
            if config.XAI_API_KEY and config.XAI_API_KEY in err_msg:
                err_msg = err_msg.replace(config.XAI_API_KEY, "[REDACTED_API_KEY]")
            logger.error("Grok API error: %s", err_msg)
            return AIResponse(
                content="",
                model=model,
                provider="grok",
                latency_ms=round(elapsed, 1),
                error=f"Grok API error: {err_msg}",
                success=False,
            )


# ── Provider Factory ─────────────────────────────────────────────────────────
def get_provider(name: str | None = None) -> AIProvider:
    """
    Factory function to get an AI provider by name.

    Args:
        name: Provider name ('ollama' or 'grok'). Defaults to config setting.

    Returns:
        An initialized AIProvider instance.

    Raises:
        ValueError: If the provider name is unknown or credentials missing.
    """
    name = (name or config.DEFAULT_PROVIDER).lower().strip()

    if name == "ollama":
        return OllamaProvider()
    elif name == "grok":
        if not config.GROK_AVAILABLE:
            raise ValueError(
                "Grok provider requires XAI_API_KEY in environment. "
                "Set it in your .env file or environment variables."
            )
        return GrokProvider()
    else:
        raise ValueError(
            f"Unknown provider '{name}'. Supported: 'ollama', 'grok'"
        )
