"""
DeadWave 13 — Configuration Module
Loads environment variables, defines defaults, and exposes typed config.
"""

from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env ────────────────────────────────────────────────────────────────
_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(_ENV_PATH)

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "deadwave.db"

# ── AI Provider Settings ─────────────────────────────────────────────────────
# "ollama" or "grok"
DEFAULT_PROVIDER: str = os.getenv("DEADWAVE_DEFAULT_PROVIDER", "ollama")

# Ollama (Local)
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_DEFAULT_MODEL: str = os.getenv("OLLAMA_DEFAULT_MODEL", "qwen2.5:3b")
OLLAMA_MODELS: list[str] = [
    "qwen2.5:3b",
    "llama3.2:1b",
    "gemma3:1b",
]

# Grok (xAI Cloud)
XAI_API_KEY: str | None = os.getenv("XAI_API_KEY")
GROK_MODEL: str = os.getenv("GROK_MODEL", "grok-3-mini")
GROK_BASE_URL: str = os.getenv("GROK_BASE_URL", "https://api.x.ai/v1")

# ── Inference Settings ────────────────────────────────────────────────────────
AI_TIMEOUT: int = int(os.getenv("AI_TIMEOUT", "60"))
MAX_CONTEXT_MESSAGES: int = int(os.getenv("MAX_CONTEXT_MESSAGES", "20"))
MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1024"))
TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.8"))

# ── Radio Settings ───────────────────────────────────────────────────────────
RADIO_MIN_FREQ: float = 88.0
RADIO_MAX_FREQ: float = 108.0
RADIO_FREQ_STEP: float = 0.1
MAX_INPUT_LENGTH: int = 500

# ── Curse Decoder Settings ────────────────────────────────────────────────────
MAX_CURSE_ATTEMPTS: int = 3
MAX_RETRIES: int = 2

# ── Application ──────────────────────────────────────────────────────────────
APP_NAME: str = "DeadWave 13"
APP_TAGLINE: str = "Tune Into the Dead. Break Their Curses."
APP_VERSION: str = "0.1.0"

# ── Derived ──────────────────────────────────────────────────────────────────
GROK_AVAILABLE: bool = bool(XAI_API_KEY and XAI_API_KEY.strip())
