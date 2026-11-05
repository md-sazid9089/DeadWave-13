"""
DeadWave 13 — Main Application
"Tune Into the Dead. Break Their Curses."

A unified Halloween / Día de los Muertos / Ghost in the Machine experience
powered by local open-weight AI (Ollama) or cloud inference (Grok via xAI).
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import streamlit as st

# Ensure project root is available for imports
_PROJECT_ROOT = Path(__file__).resolve().parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import config
from ai_provider import get_provider, AIProvider, OllamaProvider, GrokProvider
from storage import init_db, get_recent_curse_cases, get_recent_transmissions
from styles import (
    MAIN_CSS,
    render_navbar,
    render_hero,
    render_spectral_divider,
    render_footer,
)
from ghost_radio import render_ghost_radio
from curse_decoder import render_curse_decoder

# ── Logging Configuration ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DeadWave 13 — Tune Into the Dead",
    page_icon="☠️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Database Initialization ───────────────────────────────────────────────────
@st.cache_resource
def _bootstrap_db() -> bool:
    """Initialize SQLite database tables once per runtime lifecycle."""
    try:
        init_db()
        return True
    except Exception as e:
        logger.error("Database initialization failed: %s", e)
        return False


# ── Provider & Session Management ─────────────────────────────────────────────
def _init_app_state() -> None:
    """Initialize core app session state variables."""
    if "provider_name" not in st.session_state:
        st.session_state.provider_name = config.DEFAULT_PROVIDER

    if "selected_model" not in st.session_state:
        if st.session_state.provider_name == "ollama":
            st.session_state.selected_model = config.OLLAMA_DEFAULT_MODEL
        else:
            st.session_state.selected_model = config.GROK_MODEL

    if "provider_connected" not in st.session_state:
        st.session_state.provider_connected = False

    if "active_feature_tab" not in st.session_state:
        st.session_state.active_feature_tab = 0


def _get_provider_instance() -> AIProvider | None:
    """Resolve active AI provider and probe its live availability."""
    try:
        provider = get_provider(st.session_state.provider_name)
        st.session_state.provider_connected = provider.check_availability()
        return provider
    except ValueError as ve:
        logger.warning("Provider unavailable: %s", ve)
        st.session_state.provider_connected = False
        return None
    except Exception as e:
        logger.error("Unexpected error initializing provider: %s", e)
        st.session_state.provider_connected = False
        return None


# ── Sidebar Controls ──────────────────────────────────────────────────────────
def _render_sidebar(provider: AIProvider | None) -> None:
    """Render the dark control panel sidebar."""
    with st.sidebar:
        st.markdown("## ⚙️ Grimoire Controls")
        st.caption("AI Provider & Occult Resonance Settings")
        st.markdown(render_spectral_divider("CONSOLE"), unsafe_allow_html=True)

        # ── Provider Selection ────────────────────────────────────────────
        st.markdown("#### 📡 Inference Engine")
        available_providers = ["ollama"]
        if config.GROK_AVAILABLE:
            available_providers.append("grok")

        provider_labels = {
            "ollama": "🖥️ Local Ollama (Offline)",
            "grok": "☁️ Grok xAI (Cloud API)",
        }

        current_idx = (
            available_providers.index(st.session_state.provider_name)
            if st.session_state.provider_name in available_providers
            else 0
        )

        chosen_provider = st.selectbox(
            "Select Provider",
            options=available_providers,
            format_func=lambda p: provider_labels.get(p, p),
            index=current_idx,
            key="sb_provider_select",
        )

        if chosen_provider != st.session_state.provider_name:
            st.session_state.provider_name = chosen_provider
            if chosen_provider == "ollama":
                st.session_state.selected_model = config.OLLAMA_DEFAULT_MODEL
            else:
                st.session_state.selected_model = config.GROK_MODEL
            st.rerun()

        # Connection status notification
        is_conn = st.session_state.provider_connected
        if st.session_state.provider_name == "ollama":
            if is_conn:
                st.success("📡 Verified Local Inference: Offline & Private")
            else:
                st.error("❌ Ollama server unreachable (`http://localhost:11434`)")
                st.caption("Start it in terminal:\n```bash\nollama serve\n```")
        elif st.session_state.provider_name == "grok":
            st.info("☁️ Grok (xAI) active: External cloud API enabled")

        st.markdown("---")

        # ── Model Selection ───────────────────────────────────────────────
        st.markdown("#### 🤖 Model Selection")

        if provider and st.session_state.provider_name == "ollama":
            models = provider.list_models()
            model_names = [m.name for m in models]
            status_map = {m.name: m.available for m in models}

            if model_names:
                curr_model_idx = (
                    model_names.index(st.session_state.selected_model)
                    if st.session_state.selected_model in model_names
                    else 0
                )
                chosen_model = st.selectbox(
                    "Ollama Model",
                    options=model_names,
                    format_func=lambda n: f"{'✅' if status_map.get(n, False) else '❌'} {n}",
                    index=curr_model_idx,
                    key="sb_model_select",
                )
                st.session_state.selected_model = chosen_model

                if not status_map.get(chosen_model, False):
                    st.warning(
                        f"⚠️ `{chosen_model}` is not yet pulled.\n\n"
                        f"Install locally:\n```bash\nollama pull {chosen_model}\n```"
                    )
        elif st.session_state.provider_name == "grok":
            st.text_input(
                "Configured Grok Model",
                value=config.GROK_MODEL,
                disabled=True,
                key="sb_grok_display",
            )
            st.session_state.selected_model = config.GROK_MODEL

        st.markdown("---")

        # ── Telemetry & Limits ────────────────────────────────────────────
        st.markdown("#### 📊 Engine Constraints")
        st.caption(f"**App Version:** {config.APP_VERSION}")
        st.caption(f"**Inference Timeout:** {config.AI_TIMEOUT}s")
        st.caption(f"**Bounded Context:** {config.MAX_CONTEXT_MESSAGES} messages")
        st.caption(f"**Max Input:** {config.MAX_INPUT_LENGTH} chars")
        st.caption(f"**Database:** SQLite WAL (`{config.DB_PATH.name}`)")

        if not config.GROK_AVAILABLE:
            st.markdown("---")
            st.caption("💡 *Add `XAI_API_KEY` to `.env` to unlock cloud Grok.*")


# ── Recent Hauntings Section ──────────────────────────────────────────────────
def _render_recent_hauntings() -> None:
    """Render the compact historical archive of recent radio and curse events."""
    st.markdown(
        """
        <div class="hauntings-container">
            <div class="hauntings-header">
                <span>🕯️</span>
                <span>Recent Hauntings & Broken Bonds</span>
                <span>🍂</span>
            </div>
        """,
        unsafe_allow_html=True,
    )

    col_trans, col_cases = st.columns(2)

    with col_trans:
        st.markdown("##### 📻 Intercepted Signals")
        recent_trans = get_recent_transmissions(limit=4)
        if recent_trans:
            for item in recent_trans:
                freq_val = item.get("frequency", "??")
                freq_str = f"{freq_val:.1f} MHz" if isinstance(freq_val, (int, float)) else f"{freq_val} MHz"
                st.markdown(
                    f"""
                    <div class="history-chip">
                        <div style="color: #ff9500; font-weight: 600;">
                            📻 {item['ghost_name']} <span style="opacity: 0.7;">[{freq_str}]</span>
                        </div>
                        <div style="font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; color: #cbd5e1; margin-top: 0.2rem;">
                            "{item['content'][:110]}..."
                        </div>
                        <div style="font-size: 0.72rem; opacity: 0.6; margin-top: 0.3rem;">
                            ⏱️ {item['created_at']} · {item['provider']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No spectral transmissions recorded yet. Tune the dial above.")

    with col_cases:
        st.markdown("##### 🔮 Cataloged Relics")
        recent_cases = get_recent_curse_cases(limit=4)
        if recent_cases:
            for case in recent_cases:
                badge = (
                    "🟢 Solved"
                    if case["status"] == "solved"
                    else "🔴 Haunted"
                    if case["status"] == "failed"
                    else "🟡 Active"
                )
                st.markdown(
                    f"""
                    <div class="history-chip">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: #fbbf24; font-weight: 600;">{case['case_title']}</span>
                            <span style="font-size: 0.75rem;">{badge}</span>
                        </div>
                        <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.2rem;">
                            Relic: <em>{case['haunted_object']}</em>
                        </div>
                        <div style="font-size: 0.72rem; opacity: 0.6; margin-top: 0.2rem;">
                            Attempts used: {case['attempts_used']}/{config.MAX_CURSE_ATTEMPTS}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No curses decoded yet. Submit a relic above to begin.")

    st.markdown("</div>", unsafe_allow_html=True)


# ── Main Entry Point ──────────────────────────────────────────────────────────
def main() -> None:
    """Execute the DeadWave 13 single-page application."""
    # Inject styling
    st.markdown(MAIN_CSS, unsafe_allow_html=True)

    # Initialize storage & session
    _bootstrap_db()
    _init_app_state()

    # Resolve active AI provider
    provider = _get_provider_instance()

    # Render sidebar
    _render_sidebar(provider)

    # Top Navbar matching Figma
    st.markdown(
        render_navbar(
            provider_name=st.session_state.provider_name,
            is_connected=st.session_state.provider_connected,
            selected_model=st.session_state.selected_model,
        ),
        unsafe_allow_html=True,
    )

    # Hero banner
    st.markdown(render_hero(), unsafe_allow_html=True)

    # Hero Quick CTA Buttons
    cta_col1, cta_col2 = st.columns(2)
    with cta_col1:
        if st.button("📻 Enter Ghost Radio", key="cta_radio", use_container_width=True):
            st.session_state.active_feature_tab = 0
            st.rerun()

    with cta_col2:
        if st.button("🔮 Decode a Curse", key="cta_curse", use_container_width=True):
            st.session_state.active_feature_tab = 1
            st.rerun()

    st.markdown(render_spectral_divider("CHOOSE YOUR RITUAL"), unsafe_allow_html=True)

    # ── Two Main Feature Panels ───────────────────────────────────────────────
    # Streamlit tabs guarantee responsive mobile stacking and desktop switching
    tab_radio, tab_curse = st.tabs([
        "📻 Feature 1: Ghost Radio",
        "🔮 Feature 2: Curse Decoder",
    ])

    with tab_radio:
        render_ghost_radio(provider, st.session_state.selected_model)

    with tab_curse:
        render_curse_decoder(provider, st.session_state.selected_model)

    # ── Recent Hauntings Section ──────────────────────────────────────────────
    _render_recent_hauntings()

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(render_footer(), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
