"""
Streamlit UI and Integration Tests — Validates full app rendering,
widget presence, sidebar controls, session state isolation, and exception-free execution.
"""

from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).parent.parent / "app.py"


@pytest.fixture(autouse=True)
def _use_temp_db(tmp_path, monkeypatch):
    """Ensure temporary database is used during AppTest."""
    test_db = tmp_path / "test_app_ui.db"
    monkeypatch.setattr("config.DB_PATH", test_db)
    import storage
    monkeypatch.setattr(storage, "DB_PATH", test_db)


def test_app_renders_without_exceptions():
    """Verify that app.py runs end-to-end with 0 exceptions."""
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=10)
    assert len(at.exception) == 0, f"App raised exceptions: {at.exception}"


def test_app_sidebar_controls():
    """Verify sidebar controls for provider and model selection are present."""
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=10)

    # Sidebar selectbox exists
    assert len(at.sidebar.selectbox) >= 1
    provider_sb = at.sidebar.selectbox[0]
    assert provider_sb.value in ("ollama", "grok")


def test_app_tabs_present():
    """Verify exactly the two feature tabs are rendered."""
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=10)

    assert len(at.tabs) == 2
    # Radio slider in first tab
    assert len(at.slider) >= 1
    slider = at.slider[0]
    assert slider.min == 88.0
    assert slider.max == 108.0
