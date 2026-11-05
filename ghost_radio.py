"""
DeadWave 13 — Feature 1: Ghost Radio
Interactive spectral radio tuning into fictional spirits across 88.0 to 108.0 MHz.
Features deterministic frequency mapping, isolated per-ghost conversation memories,
SQLite persistence, and bounded context LLM inference.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

import streamlit as st

import config
from ai_provider import AIProvider, AIResponse
from prompts import (
    ALL_GHOSTS,
    GhostPersona,
    get_ghost_by_frequency,
    GHOST_RADIO_TRANSMIT_PROMPT,
    GHOST_RADIO_MESSAGE_PROMPT,
)
from storage import create_session, save_message, clear_session_messages
from styles import render_spectral_divider

logger = logging.getLogger(__name__)


def _init_radio_session() -> None:
    """Initialize Streamlit session state for Ghost Radio."""
    if "radio_session_base_id" not in st.session_state:
        st.session_state.radio_session_base_id = str(uuid.uuid4())[:8]

    if "radio_frequency" not in st.session_state:
        st.session_state.radio_frequency = 88.0

    # Separate memory per ghost name
    if "ghost_memories" not in st.session_state:
        st.session_state.ghost_memories = {g.name: [] for g in ALL_GHOSTS}

    # Ensure all ghosts have a list
    for g in ALL_GHOSTS:
        if g.name not in st.session_state.ghost_memories:
            st.session_state.ghost_memories[g.name] = []


def _get_ghost_session_id(ghost_name: str) -> str:
    """Generate isolated session ID for a specific ghost."""
    base = st.session_state.radio_session_base_id
    safe_name = ghost_name.lower().replace(" ", "_")
    return f"radio_{safe_name}_{base}"


def render_ghost_radio(provider: AIProvider | None, selected_model: str) -> None:
    """
    Render the Ghost Radio interface.

    Args:
        provider: Active AI provider instance or None if unconfigured.
        selected_model: Name of the selected model.
    """
    _init_radio_session()

    st.markdown("### 📻 Spectral Radio Receiver")
    st.caption("Tune the dial between 88.0 and 108.0 MHz to pierce the electromagnetic veil.")

    # ── Frequency Dial ────────────────────────────────────────────────────
    new_freq = st.slider(
        "Frequency Dial (MHz)",
        min_value=config.RADIO_MIN_FREQ,
        max_value=config.RADIO_MAX_FREQ,
        value=float(st.session_state.radio_frequency),
        step=config.RADIO_FREQ_STEP,
        format="%.1f MHz",
        key="radio_freq_slider",
        help="Turn the dial across the spectrum to reach different lingering spirits.",
    )
    st.session_state.radio_frequency = round(new_freq, 1)
    current_freq = st.session_state.radio_frequency

    # Deterministically resolve ghost persona
    ghost: GhostPersona = get_ghost_by_frequency(current_freq)
    ghost_memory = st.session_state.ghost_memories[ghost.name]
    session_id = _get_ghost_session_id(ghost.name)

    # ── Vintage Glowing LED Display ───────────────────────────────────────
    # Signal strength calculation based on frequency offset from ghost center
    freq_range_center = (ghost.min_freq + ghost.max_freq) / 2.0
    dist = abs(current_freq - freq_range_center)
    if dist < 0.8:
        signal_bars = "SIGNAL: ■■■■■ RESONANCE PEAK"
        signal_color = "#34d399"
    elif dist < 1.6:
        signal_bars = "SIGNAL: ■■■□□ MODERATE OSCILLATION"
        signal_color = "#fbbf24"
    else:
        signal_bars = "SIGNAL: ■□□□□ FRINGE STATIC"
        signal_color = "#a855f7"

    display_html = f"""
    <div class="frequency-display-panel">
        <p class="frequency-led">[ {current_freq:.1f} MHz ]</p>
        <div class="signal-meter" style="color: {signal_color};">
            <span>{ghost.ambient_symbol}</span>
            <span>{signal_bars}</span>
            <span>{ghost.ambient_symbol}</span>
        </div>
    </div>
    """
    st.markdown(display_html, unsafe_allow_html=True)

    # ── Ghost Persona Card ────────────────────────────────────────────────
    persona_html = f"""
    <div class="persona-card">
        <div class="persona-header">
            <span class="persona-icon">{ghost.avatar_icon}</span>
            <div>
                <p class="persona-title">{ghost.name}</p>
                <span class="persona-epithet">{ghost.epithet} · Channel {ghost.min_freq:.1f}–{ghost.max_freq:.1f} MHz</span>
            </div>
        </div>
        <p style="margin: 0.3rem 0; font-size: 0.9rem; color: #cbd5e1;"><strong>Era:</strong> {ghost.era}</p>
        <p style="margin: 0.3rem 0; font-size: 0.88rem; color: #94a3b8; line-height: 1.4;">{ghost.backstory}</p>
        <p style="margin: 0.3rem 0; font-size: 0.82rem; color: #a855f7;"><strong>Style:</strong> {ghost.speaking_style}</p>
        <div class="persona-mystery">
            <strong>Paranormal Mystery:</strong> {ghost.mystery}
        </div>
    </div>
    """
    st.markdown(persona_html, unsafe_allow_html=True)

    # ── Primary Actions: Receive Transmission & Reset ─────────────────────
    col_trans, col_reset = st.columns([3, 1])

    with col_trans:
        receive_clicked = st.button(
            "⚡ Receive Transmission",
            key=f"receive_btn_{ghost.name}_{current_freq}",
            use_container_width=True,
            help="Listen for incoming radio static and words from this entity.",
        )

    with col_reset:
        reset_clicked = st.button(
            "🔄 Clear Tape",
            key=f"reset_btn_{ghost.name}",
            use_container_width=True,
            help="Clear this ghost's recorded memory tape.",
        )

    if reset_clicked:
        st.session_state.ghost_memories[ghost.name] = []
        try:
            clear_session_messages(session_id)
        except Exception as e:
            logger.warning("Could not clear session in db: %s", e)
        st.toast(f"Memory tape cleared for {ghost.name}.", icon="🧹")
        st.rerun()

    # Handle "Receive Transmission" trigger
    if receive_clicked:
        if not provider:
            st.error("No AI provider is connected. Check your Ollama or Grok configuration in the sidebar.")
        else:
            with st.spinner(f"░▒▓ Intercepting {ghost.name}'s frequency at {current_freq:.1f} MHz... ▓▒░"):
                messages = [
                    {"role": "system", "content": ghost.system_prompt},
                ]
                # Include bounded previous conversation
                for m in ghost_memory[-config.MAX_CONTEXT_MESSAGES:]:
                    messages.append({"role": m["role"], "content": m["content"]})

                # Prompt for new transmission
                prompt_content = GHOST_RADIO_TRANSMIT_PROMPT.format(
                    frequency=current_freq,
                    ghost_name=ghost.name,
                    epithet=ghost.epithet,
                )
                messages.append({"role": "user", "content": prompt_content})

                response: AIResponse = provider.generate(
                    messages=messages,
                    model=selected_model,
                )

                if response.success and response.content.strip():
                    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
                    msg_obj = {
                        "role": "assistant",
                        "content": response.content.strip(),
                        "timestamp": ts,
                        "frequency": current_freq,
                    }
                    st.session_state.ghost_memories[ghost.name].append(msg_obj)

                    # Persist to SQLite
                    try:
                        create_session(
                            session_id,
                            "ghost_radio",
                            provider.provider_name,
                            selected_model,
                        )
                        save_message(
                            session_id,
                            "assistant",
                            response.content.strip(),
                            metadata={
                                "frequency": current_freq,
                                "ghost_name": ghost.name,
                                "latency_ms": response.latency_ms,
                                "tokens": response.tokens_used,
                            },
                        )
                    except Exception as e:
                        logger.error("Failed to persist ghost transmission: %s", e)
                    st.rerun()
                else:
                    st.error(f"📡 Transmission failed: {response.error or 'No response received'}")

    # ── Display Conversation History ──────────────────────────────────────
    if ghost_memory:
        st.markdown(f"**Recorded Transmissions ({len(ghost_memory)}):**")
        for m in ghost_memory:
            role_label = ghost.name if m["role"] == "assistant" else "Investigator"
            bubble_class = "ghost" if m["role"] == "assistant" else "user"
            ts_label = m.get("timestamp", "")
            freq_label = f"[{m.get('frequency', current_freq):.1f} MHz] " if m["role"] == "assistant" else ""

            st.markdown(
                f"""
                <div class="transmission-bubble {bubble_class}">
                    <div style="font-size: 0.78rem; opacity: 0.7; margin-bottom: 0.2rem;">
                        {freq_label}{role_label} · {ts_label}
                    </div>
                    <div>{m['content']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Transmit Back to the Ghost (Form) ─────────────────────────────────
    st.markdown(render_spectral_divider("TRANSMIT INTO VOID"), unsafe_allow_html=True)

    with st.form(key=f"radio_speak_form_{ghost.name}", clear_on_submit=True):
        user_text = st.text_input(
            f"Speak into the microphone on {current_freq:.1f} MHz:",
            max_chars=config.MAX_INPUT_LENGTH,
            placeholder=f"Address {ghost.name}...",
        )
        submit_btn = st.form_submit_button("🎙️ Transmit Voice", use_container_width=True)

    if submit_btn:
        if not user_text or not user_text.strip():
            st.warning("The microphone picked up only silence.")
        elif not provider:
            st.error("No active AI provider. Check Ollama or Grok configuration.")
        else:
            clean_input = user_text.strip()[:config.MAX_INPUT_LENGTH]
            ts = datetime.now(timezone.utc).strftime("%H:%M:%S")

            # Store user message immediately
            user_msg_obj = {
                "role": "user",
                "content": clean_input,
                "timestamp": ts,
            }
            st.session_state.ghost_memories[ghost.name].append(user_msg_obj)

            with st.spinner(f"░▒▓ Channeling response from {ghost.name}... ▓▒░"):
                messages = [
                    {"role": "system", "content": ghost.system_prompt},
                ]
                for m in ghost_memory[-config.MAX_CONTEXT_MESSAGES:]:
                    messages.append({"role": m["role"], "content": m["content"]})

                formatted_user_prompt = GHOST_RADIO_MESSAGE_PROMPT.format(
                    frequency=current_freq,
                    ghost_name=ghost.name,
                    epithet=ghost.epithet,
                    user_input=clean_input,
                )
                messages.append({"role": "user", "content": formatted_user_prompt})

                response: AIResponse = provider.generate(
                    messages=messages,
                    model=selected_model,
                )

                if response.success and response.content.strip():
                    resp_ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
                    resp_obj = {
                        "role": "assistant",
                        "content": response.content.strip(),
                        "timestamp": resp_ts,
                        "frequency": current_freq,
                    }
                    st.session_state.ghost_memories[ghost.name].append(resp_obj)

                    # Persist to database
                    try:
                        create_session(
                            session_id,
                            "ghost_radio",
                            provider.provider_name,
                            selected_model,
                        )
                        save_message(session_id, "user", clean_input)
                        save_message(
                            session_id,
                            "assistant",
                            response.content.strip(),
                            metadata={
                                "frequency": current_freq,
                                "ghost_name": ghost.name,
                                "latency_ms": response.latency_ms,
                                "tokens": response.tokens_used,
                            },
                        )
                    except Exception as e:
                        logger.error("Failed to save ghost dialogue: %s", e)
                    st.rerun()
                else:
                    # Provide helpful error without wiping user message
                    st.error(f"📡 Ghost transmission severed: {response.error or 'Unknown error'}")
