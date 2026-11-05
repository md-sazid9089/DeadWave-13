# ☠️ DeadWave 13

> **"Tune Into the Dead. Break Their Curses."**  
> *A Paranormal AI-Powered Halloween & Día de los Muertos Experience*

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.66+-red.svg)](https://streamlit.io/)
[![Ollama](https://img.shields.io/badge/Ollama-Offline%20AI-orange.svg)](https://ollama.ai/)
[![xAI Grok](https://img.shields.io/badge/xAI-Grok%20Cloud-black.svg)](https://x.ai/)
[![Tests](https://img.shields.io/badge/Tests-49%20Passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎃 1. Project Overview

**DeadWave 13** is a production-grade, Python-only AI web application designed for a Halloween / Día de los Muertos hackathon. Operating as a single unified homepage, it transports the user into the paranormal realm through two dedicated experiences:

1. **Ghost Radio**: A spectral frequency scanner (88.0–108.0 MHz) channeling 5 distinct fictional spirits across time.
2. **Curse Decoder**: An interactive deductive occult mystery game where players inspect cursed relics, receive structured riddles, and break ancient curses before their life candles extinguish.

---

## 🕯️ 2. Halloween / Día de los Muertos Concept

DeadWave 13 blends Victorian ghost mythology, maritime legends, early 20th-century radio mysteries, and Mexican Día de los Muertos traditions into an eerie, immersive "Ghost in the Machine" aesthetic:
- **Warm Candlelight Highlights** (`#fbbf24`) and **Marigold Accents** (`#ff7700`) evoke the ofrenda and cempasúchil petals.
- **Deep Violet / Near-Black Backdrop** (`#08040f` to `#13091f`) simulates late-night airwaves.
- **Glowing Vacuum Tubes & Monospace Telemetry** capture vintage shortwave radio communication.

---

## ⚡ 3. Feature Breakdown

### 📻 Feature 1: Ghost Radio
- **Interactive Frequency Dial**: 88.0 MHz to 108.0 MHz (step 0.1 MHz) with glowing LED frequency readout.
- **5 Unique Fictional Spirits**:
  - `88.0–91.9 MHz`: **Arthur Vance** ("The Lost Broadcaster", 1938) — Searching for the lost 13 seconds of his final storm broadcast.
  - `92.0–95.9 MHz`: **Isabella Vega** ("The Midnight Bride", 1887) — Mournful bilingual spirit of Día de los Muertos altars.
  - `96.0–99.9 MHz`: **Captain Thaddeus Graves** ("The Forgotten Sailor", 1899) — Salt-encrusted skipper of the drowned ironclad *Nautilus 13*.
  - `100.0–103.9 MHz`: **Silas Pendelton** ("The Clockmaker", 1874) — Neurotic horologist whose pulse stopped at 12:13 AM.
  - `104.0–108.0 MHz`: **Ignacio Morales** ("The Cemetery Keeper", 1954) — Earth-worn guardian of Grave 0 at San Lázaro Pantheón.
- **Deterministic Boundary Mapping**: Boundary values transition smoothly and out-of-range frequencies clamp safely.
- **Per-Ghost Memory Isolation**: Tuning the dial loads that ghost's specific dialogue history without cross-contamination.
- **Safety Constraints**: Spirits strictly identify as fictional roleplay entities, never claiming to be real deceased people or genuine paranormal conduits.

### 🔮 Feature 2: Curse Decoder
- **Interactive Deductive Mystery Game**: Enter any haunted relic (e.g., an antique silver hand-mirror, a bloodstained music box).
- **Structured Pydantic Case File**: Generates an atmospheric title, supernatural affliction, backstory, puzzle riddle, initial clue, progressive hints, and secret solution.
- **Solution Leak Detection**: Automated security scanning ensures the model never leaks the answer inside visible clues.
- **Deterministic Python Grading**: Normalized for unicode (NFKD), accents, case, and punctuation. No substring false positives (e.g., "key" will not match "donkey").
- **3-Attempt Candle System**:
  - Attempt 1 failure: Extinguishes 1st candle, unlocks **Hint 1**.
  - Attempt 2 failure: Extinguishes 2nd candle, unlocks **Hint 2**.
  - Attempt 3 failure: Extinguishes 3rd candle, triggers **STILL HAUNTED 💀** game over and reveals the lost solution.
  - Correct guess: Triggers **CURSE BROKEN ⚡** with supernatural resolution.

### 📜 Supporting Element: Recent Hauntings
- A persistent SQLite history archive displaying recent spectral radio transmissions and completed curse investigations with timestamps and status badges.

---

## 🎨 4. Design & Figma Reference

The interface strictly matches the DeadWave 13 Figma Make design specifications:
- **Top Navigation Bar**: DeadWave 13 wordmark, ghost icon, dynamic provider status pill, model tag.
- **Hero Section**: High-contrast typography and quick CTA focus buttons.
- **Dual Feature Panels**: Responsive tabs with side-by-side or stacked view.
- **Figma Design Reference**: [DeadWave 13 Figma Design System](https://www.figma.com/) *(Design token values implemented in `styles.py`)*.

---

## 🏗️ 5. Architecture

```
DeadWave-13/
├── app.py                # Main Streamlit web application & routing
├── config.py             # Environment config, constants & limits
├── ai_provider.py        # Abstract AIProvider (Ollama & Grok implementations)
├── ghost_radio.py        # Feature 1: Frequency slider, personas, transmission flow
├── curse_decoder.py      # Feature 2: Case generation, validation, 3-attempt game loop
├── storage.py            # SQLite persistence layer (WAL mode, sessions & curses)
├── styles.py             # Custom CSS, glowing LED styling, dark glass themes
├── prompts.py            # Personas, system prompts, puzzle schemas & templates
├── requirements.txt      # Production dependencies
├── .env.example          # Environment variable template
├── .gitignore            # Git exclusion rules
├── VERIFICATION_REPORT.md# QA lead verification audit report
├── DEMO_SCRIPT.md        # 60–90 second live demonstration script
└── tests/                # Automated pytest test suite (49 tests)
    ├── test_config.py
    ├── test_ai_provider.py
    ├── test_prompts.py
    ├── test_storage.py
    ├── test_ghost_radio.py
    ├── test_curse_decoder.py
    └── test_ui_app.py
```

---

## 🔓 6. Why Open-Weight AI Matters

DeadWave 13 champions **local open-weight AI (Ollama)**:
1. **100% Offline & Private**: Conversations with spirits and cursed mysteries never leave your computer.
2. **Zero API Cost & Rate Limits**: Run unlimited radio conversations and puzzle generations without per-token charges or subscriptions.
3. **Resilience & Censorship-Resistance**: Offline local execution operates during internet outages or air-gapped environments.
4. **Transparent Weights**: Supported models (`qwen2.5:3b`, `llama3.2:1b`, `gemma3:1b`) allow full inspection and local tuning.

---

## 💻 7. Hardware & Model Requirements

| Model | Parameters | VRAM / RAM | Recommended GPU |
| :--- | :--- | :--- | :--- |
| **qwen2.5:3b** *(Default)* | 3 Billion | ~2.5 GB | NVIDIA GTX 1650+ / Apple M1+ / CPU |
| **llama3.2:1b** | 1 Billion | ~1.3 GB | Integrated graphics / CPU |
| **gemma3:1b** | 1 Billion | ~1.5 GB | Integrated graphics / CPU |

---

## 🪟 8. Windows Installation & Setup Guide

### Step 1: Open PowerShell
Clone or navigate to the repository directory:
```powershell
cd d:\DeadWave-13
```

### Step 2: Virtual Environment Setup
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🦙 9. Ollama Installation & Model Commands

1. Download Ollama for Windows from [ollama.ai/download](https://ollama.ai/download).
2. Start the Ollama background daemon:
   ```bash
   ollama serve
   ```
3. Pull the default DeadWave 13 model:
   ```bash
   ollama pull qwen2.5:3b
   ```
4. Optional alternative lightweight models:
   ```bash
   ollama pull llama3.2:1b
   ollama pull gemma3:1b
   ```

---

## ☁️ 10. Optional Grok (xAI) Configuration

To enable cloud inference via Grok:
1. Copy the environment template:
   ```powershell
   copy .env.example .env
   ```
2. Edit `.env` and set your xAI API key:
   ```ini
   XAI_API_KEY=xai-your-api-key-here
   GROK_MODEL=grok-3-mini
   ```
3. Grok will immediately appear in the sidebar selector without requiring an application restart.

---

## 🚀 11. Running the Application

Launch the Streamlit server:
```powershell
streamlit run app.py
```
Open your browser to: **`http://localhost:8501`**

---

## 🧪 12. Running Tests

Run the complete 49-test suite:
```powershell
python -m pytest tests/ -v
```

---

## 🔧 13. Troubleshooting

- **Ollama says "Server unreachable"**:
  Make sure Ollama is running (`ollama serve` in a terminal) and listening on `http://localhost:11434`.
- **Model not found warning in sidebar**:
  Run `ollama pull qwen2.5:3b` to download the missing weights.
- **Grok option disabled in sidebar**:
  Verify `XAI_API_KEY` is defined in your `.env` file and non-empty.

---

## 🛡️ 14. Local vs. Cloud Privacy Disclosure

- **Local Mode (Ollama)**:
  - The UI displays: `● Running locally — offline`
  - **No telemetry, zero cloud calls, zero logs leaving your device.**
- **Cloud Mode (Grok xAI)**:
  - The UI displays: `☁️ Grok (xAI) — external API`
  - Transmissions are transmitted over HTTPS to `api.x.ai` subject to xAI's privacy policy.

---

## ⚠️ 15. Known Limitations & Verification Status

- **Automated Test Coverage**: 49 tests passing (100% pass rate) across configuration, AI provider abstraction, prompt templates, SQLite storage, Ghost Radio boundary & memory logic, Curse Decoder grading & leak detection, and Streamlit `AppTest` UI lifecycle.
- **Local Ollama Daemon Status**: In the current test environment, live inference was marked **BLOCKED** because the Ollama desktop daemon was not running on `localhost:11434`. The application handles this offline condition gracefully with clear notifications.
- **Cloud Grok Status**: Marked **NOT TESTED** because an `XAI_API_KEY` was not configured in `.env`.
- **Offline Safety**: Automated tests mock model calls to avoid accidental paid API usage and ensure reproducible testing.

---

## 📜 16. License & Model Acknowledgments

- **Application Code**: Licensed under the [MIT License](LICENSE).
- **Qwen 2.5**: Developed by Alibaba Cloud (Qwen Research License).
- **Llama 3.2**: Developed by Meta (Meta Llama 3 Community License).
- **Gemma 3**: Developed by Google DeepMind (Gemma Terms of Use).
