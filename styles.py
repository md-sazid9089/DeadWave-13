"""
DeadWave 13 — UI Styles & Theming System
Production-grade Streamlit CSS providing a Halloween / Día de los Muertos / Ghost in the Machine aesthetic.
Near-black & deep violet background, marigold-orange accents, soft purple spectral glow,
and vintage radio / ancient parchment styling.
"""

from __future__ import annotations

# ── Main Theme CSS ────────────────────────────────────────────────────────────
MAIN_CSS = """
<style>
    /* ── Typography & Google Fonts ────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;900&family=Share+Tech+Mono&family=Inter:wght@400;500;600;700&display=swap');

    /* ── Global Background & Base ─────────────────────────────── */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #170b2e 0%, #0d061c 45%, #05020a 100%) !important;
        color: #e2e8f0;
        font-family: 'Inter', -apple-system, sans-serif;
    }

    /* Remove excessive default padding */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1280px !important;
    }

    /* ── Top Navigation Bar ───────────────────────────────────── */
    .deadwave-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(18, 10, 32, 0.75);
        border: 1px solid rgba(255, 119, 0, 0.25);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5), inset 0 0 15px rgba(168, 85, 247, 0.15);
        border-radius: 12px;
        padding: 0.8rem 1.4rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
    }

    .deadwave-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .deadwave-brand .logo-icon {
        font-size: 1.8rem;
        filter: drop-shadow(0 0 10px rgba(255, 119, 0, 0.7));
    }

    .deadwave-brand .title {
        font-family: 'Cinzel', serif;
        font-size: 1.4rem;
        font-weight: 900;
        letter-spacing: 2.5px;
        color: #ff7700;
        text-shadow: 0 0 15px rgba(255, 119, 0, 0.5);
        margin: 0;
    }

    .deadwave-nav-badges {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    /* ── Hero Section ─────────────────────────────────────────── */
    .deadwave-hero {
        text-align: center;
        padding: 1.8rem 1rem 1.4rem 1rem;
        margin-bottom: 1.5rem;
        background: linear-gradient(180deg, rgba(30, 15, 55, 0.4) 0%, rgba(13, 6, 28, 0.1) 100%);
        border-radius: 16px;
        border-bottom: 1px solid rgba(255, 119, 0, 0.2);
    }

    .deadwave-hero h1 {
        font-family: 'Cinzel', serif;
        font-size: 2.5rem;
        font-weight: 900;
        color: #ff7700;
        text-shadow: 0 0 25px rgba(255, 119, 0, 0.6), 0 0 50px rgba(168, 85, 247, 0.4);
        margin-bottom: 0.5rem;
        letter-spacing: 2px;
    }

    .deadwave-hero .subtitle {
        font-family: 'Inter', sans-serif;
        color: #cbd5e1;
        font-size: 1.05rem;
        max-width: 780px;
        margin: 0 auto 0.5rem auto;
        line-height: 1.5;
    }

    /* ── Status Indicators ────────────────────────────────────── */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.8rem;
        border-radius: 9999px;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.82rem;
        letter-spacing: 0.5px;
        font-weight: 600;
    }

    .status-badge.online-local {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34d399;
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.2);
    }

    .status-badge.offline-local {
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.4);
        color: #f87171;
    }

    .status-badge.cloud-grok {
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.4);
        color: #fbbf24;
        box-shadow: 0 0 12px rgba(245, 158, 11, 0.2);
    }

    /* ── Vintage Radio Component ──────────────────────────────── */
    .radio-chassis {
        background: rgba(18, 11, 32, 0.85);
        border: 2px solid rgba(255, 119, 0, 0.35);
        border-radius: 14px;
        padding: 1.4rem;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.6), inset 0 0 20px rgba(255, 119, 0, 0.08);
        backdrop-filter: blur(8px);
        margin-bottom: 1.2rem;
    }

    .frequency-display-panel {
        background: #040108;
        border: 2px solid #ff7700;
        border-radius: 10px;
        padding: 1rem 1.4rem;
        text-align: center;
        box-shadow: inset 0 0 25px rgba(255, 119, 0, 0.25), 0 0 20px rgba(255, 119, 0, 0.2);
        margin: 0.8rem 0;
    }

    .frequency-led {
        font-family: 'Share Tech Mono', monospace;
        font-size: 2.8rem;
        font-weight: 700;
        color: #ff9500;
        text-shadow: 0 0 15px rgba(255, 149, 0, 0.8), 0 0 30px rgba(255, 119, 0, 0.4);
        letter-spacing: 3px;
        margin: 0;
    }

    .signal-meter {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.5rem;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.85rem;
        color: #a855f7;
        margin-top: 0.4rem;
        letter-spacing: 1px;
    }

    /* ── Ghost Persona Card ───────────────────────────────────── */
    .persona-card {
        background: linear-gradient(135deg, rgba(32, 17, 56, 0.7) 0%, rgba(18, 9, 32, 0.85) 100%);
        border: 1px solid rgba(168, 85, 247, 0.35);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), inset 0 0 15px rgba(168, 85, 247, 0.1);
    }

    .persona-header {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 0.6rem;
    }

    .persona-icon {
        font-size: 2rem;
        background: rgba(255, 119, 0, 0.15);
        border: 1px solid rgba(255, 119, 0, 0.3);
        padding: 0.3rem 0.6rem;
        border-radius: 8px;
    }

    .persona-title {
        font-family: 'Cinzel', serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: #ff9500;
        margin: 0;
    }

    .persona-epithet {
        font-family: 'Share Tech Mono', monospace;
        color: #c084fc;
        font-size: 0.85rem;
    }

    .persona-mystery {
        background: rgba(10, 5, 20, 0.6);
        border-left: 3px solid #ff7700;
        padding: 0.6rem 0.9rem;
        font-size: 0.85rem;
        color: #e2e8f0;
        border-radius: 0 6px 6px 0;
        margin-top: 0.7rem;
    }

    /* ── Radio Transmission Stream ────────────────────────────── */
    .transmission-bubble {
        background: rgba(14, 8, 25, 0.75);
        border: 1px solid rgba(255, 119, 0, 0.2);
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        margin: 0.6rem 0;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.92rem;
        line-height: 1.5;
    }

    .transmission-bubble.ghost {
        border-left: 3px solid #a855f7;
        color: #e9d5ff;
        background: linear-gradient(90deg, rgba(35, 16, 62, 0.4) 0%, rgba(14, 8, 25, 0.75) 100%);
    }

    .transmission-bubble.user {
        border-left: 3px solid #ff7700;
        color: #fed7aa;
        background: linear-gradient(90deg, rgba(45, 22, 10, 0.35) 0%, rgba(14, 8, 25, 0.75) 100%);
    }

    /* ── Ancient Curse Parchment ──────────────────────────────── */
    .curse-card {
        background: linear-gradient(135deg, rgba(28, 14, 46, 0.85) 0%, rgba(16, 8, 28, 0.95) 100%);
        border: 2px solid rgba(245, 158, 11, 0.35);
        border-radius: 14px;
        padding: 1.4rem;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.6), inset 0 0 20px rgba(245, 158, 11, 0.08);
        margin-bottom: 1.2rem;
    }

    .curse-title {
        font-family: 'Cinzel', serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #fbbf24;
        text-shadow: 0 0 15px rgba(251, 191, 36, 0.5);
        margin: 0 0 0.8rem 0;
        text-align: center;
    }

    .candle-tracker {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.6rem;
        font-size: 1.4rem;
        margin: 0.8rem 0;
    }

    .puzzle-box {
        background: rgba(9, 4, 18, 0.8);
        border: 1px dashed rgba(251, 191, 36, 0.4);
        border-radius: 10px;
        padding: 1.1rem;
        margin: 1rem 0;
    }

    .puzzle-question {
        font-family: 'Cinzel', serif;
        font-size: 1.05rem;
        color: #fef08a;
        margin-bottom: 0.5rem;
    }

    .clue-tag {
        display: inline-block;
        background: rgba(168, 85, 247, 0.2);
        border: 1px solid rgba(168, 85, 247, 0.4);
        color: #e9d5ff;
        padding: 0.3rem 0.7rem;
        border-radius: 6px;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }

    .curse-solved-banner {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.3) 100%);
        border: 2px solid #10b981;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        color: #a7f3d0;
        box-shadow: 0 0 25px rgba(16, 185, 129, 0.3);
        margin: 1rem 0;
    }

    .curse-failed-banner {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(185, 28, 28, 0.3) 100%);
        border: 2px solid #ef4444;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        color: #fca5a5;
        box-shadow: 0 0 25px rgba(239, 68, 68, 0.3);
        margin: 1rem 0;
    }

    /* ── Recent Hauntings Section ─────────────────────────────── */
    .hauntings-container {
        background: rgba(15, 8, 26, 0.6);
        border: 1px solid rgba(255, 119, 0, 0.2);
        border-radius: 14px;
        padding: 1.4rem;
        margin-top: 2rem;
    }

    .hauntings-header {
        font-family: 'Cinzel', serif;
        font-size: 1.3rem;
        color: #ff9500;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }

    .history-chip {
        background: rgba(25, 13, 44, 0.7);
        border: 1px solid rgba(168, 85, 247, 0.2);
        border-radius: 8px;
        padding: 0.7rem 0.9rem;
        margin-bottom: 0.6rem;
        font-size: 0.85rem;
    }

    /* ── Buttons & Streamlit Inputs ───────────────────────────── */
    .stButton > button {
        background: linear-gradient(135deg, #ff7700 0%, #ea580c 100%) !important;
        color: #ffffff !important;
        font-family: 'Share Tech Mono', monospace !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.2rem !important;
        box-shadow: 0 4px 15px rgba(255, 119, 0, 0.35) !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        box-shadow: 0 6px 25px rgba(255, 119, 0, 0.6) !important;
        transform: translateY(-2px) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* Secondary buttons */
    button[kind="secondary"] {
        background: rgba(30, 16, 50, 0.8) !important;
        border: 1px solid rgba(168, 85, 247, 0.4) !important;
        color: #c084fc !important;
    }

    /* Inputs */
    .stTextInput input, .stTextArea textarea {
        background: rgba(10, 4, 18, 0.85) !important;
        border: 1px solid rgba(255, 119, 0, 0.3) !important;
        color: #f1f5f9 !important;
        border-radius: 8px !important;
        font-family: 'Share Tech Mono', monospace !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #ff7700 !important;
        box-shadow: 0 0 10px rgba(255, 119, 0, 0.4) !important;
    }

    /* ── Footer ───────────────────────────────────────────────── */
    .deadwave-footer {
        text-align: center;
        padding: 2rem 1rem 1rem 1rem;
        margin-top: 3rem;
        border-top: 1px solid rgba(255, 119, 0, 0.2);
        color: #64748b;
        font-size: 0.82rem;
        font-family: 'Share Tech Mono', monospace;
    }

    .deadwave-footer .manifesto {
        font-size: 1rem;
        color: #ff9500;
        font-family: 'Cinzel', serif;
        margin-bottom: 0.4rem;
        letter-spacing: 2px;
    }
</style>
"""


# ── Component Helpers ─────────────────────────────────────────────────────────
def render_navbar(provider_name: str, is_connected: bool, selected_model: str) -> str:
    """Render top navigation bar matching the dark premium Figma design."""
    if provider_name == "ollama":
        if is_connected:
            badge_html = '<span class="status-badge online-local">● Running locally — offline</span>'
        else:
            badge_html = '<span class="status-badge offline-local">○ Ollama unavailable</span>'
    elif provider_name == "grok":
        badge_html = '<span class="status-badge cloud-grok">☁️ Grok (xAI) — external API</span>'
    else:
        badge_html = '<span class="status-badge offline-local">○ Provider unconfigured</span>'

    return f"""
    <div class="deadwave-nav">
        <div class="deadwave-brand">
            <span class="logo-icon">☠️</span>
            <div>
                <p class="title">DEADWAVE 13</p>
            </div>
        </div>
        <div class="deadwave-nav-badges">
            {badge_html}
            <span style="font-family: 'Share Tech Mono', monospace; font-size: 0.82rem; color: #94a3b8;">
                [{selected_model}]
            </span>
        </div>
    </div>
    """


def render_hero() -> str:
    """Render the hero title and evocative subtitle."""
    return """
    <div class="deadwave-hero">
        <h1>Tune Into the Dead. Break Their Curses.</h1>
        <p class="subtitle">
            An AI-powered Halloween experience where forgotten spirits transmit their stories
            across spectral radio waves, and cursed occult mysteries await your answers.
        </p>
    </div>
    """


def render_spectral_divider(label: str = "DEADWAVE 13") -> str:
    """Render an aesthetic divider with ASCII static decoration."""
    return f"""
    <div style="text-align: center; color: rgba(255, 119, 0, 0.4); font-family: 'Share Tech Mono', monospace; font-size: 0.78rem; margin: 1.2rem 0; letter-spacing: 3px;">
        ░▒▓█ {label} █▓▒░
    </div>
    """


def render_footer() -> str:
    """Render the privacy-respecting footer disclosure."""
    return """
    <div class="deadwave-footer">
        <p class="manifesto">Open-weight. Private. Yours.</p>
        <p>
            Local Ollama mode runs 100% offline on your device with no telemetry.
            Cloud Grok mode routes prompts via the official xAI API.
        </p>
        <p style="margin-top: 0.3rem; opacity: 0.7;">
            DeadWave 13 · Halloween & Día de los Muertos Edition · Built with Python & Streamlit
        </p>
    </div>
    """
