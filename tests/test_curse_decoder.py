"""
Tests for Curse Decoder — Schema Validation, Normalization, Deterministic Grading,
Hint Progression, Solution Leak Detection, and AI Generation Retries.
"""

import json
import pytest
from unittest.mock import MagicMock
from pydantic import ValidationError

from ai_provider import AIProvider, AIResponse
from curse_decoder import (
    CurseCase,
    normalize_answer,
    check_answer,
    detect_solution_leakage,
    generate_curse_puzzle,
)
from storage import (
    init_db,
    save_curse_case,
    update_curse_status,
    get_recent_curse_cases,
)


@pytest.fixture(autouse=True)
def _use_temp_db(tmp_path, monkeypatch):
    """Redirect DB_PATH to a temporary database file."""
    test_db = tmp_path / "test_deadwave.db"
    monkeypatch.setattr("config.DB_PATH", test_db)
    import storage
    monkeypatch.setattr(storage, "DB_PATH", test_db)
    init_db()


# ── Normalization Tests ───────────────────────────────────────────────────────
def test_normalize_answer_whitespace():
    """Whitespace should be trimmed and multiple spaces collapsed."""
    assert normalize_answer("   silver    key   ") == "silver key"
    assert normalize_answer("\tbell\n") == "bell"


def test_normalize_answer_case_and_punctuation():
    """Should convert to lowercase and strip all punctuation."""
    assert normalize_answer("SILVER-KEY!") == "silver key"
    assert normalize_answer("'Marigold'...") == "marigold"
    assert normalize_answer("Salt & Iron.") == "salt iron"


def test_normalize_answer_unicode_accents():
    """Diacritics and accents should be cleanly stripped."""
    assert normalize_answer("cempasúchil") == "cempasuchil"
    assert normalize_answer("clavier hanté") == "clavier hante"
    assert normalize_answer("añejo") == "anejo"


def test_normalize_answer_empty():
    """Empty or None input should return empty string."""
    assert normalize_answer("") == ""
    assert normalize_answer("   ") == ""


# ── Deterministic Answer Checking Tests ───────────────────────────────────────
def test_check_answer_canonical_exact():
    """Exact canonical match should succeed."""
    assert check_answer("silver key", "silver key") is True
    assert check_answer("SILVER KEY", "silver key") is True
    assert check_answer(" silver key! ", "silver key") is True


def test_check_answer_aliases():
    """Matching against accepted aliases should succeed."""
    canonical = "marigold"
    aliases = ["marigolds", "cempasuchil", "cempasúchil", "flor de muerto"]

    assert check_answer("marigolds", canonical, aliases) is True
    assert check_answer("cempasúchil", canonical, aliases) is True
    assert check_answer("flor de muerto", canonical, aliases) is True
    assert check_answer("rose", canonical, aliases) is False


def test_check_answer_no_substring_false_positive():
    """Substring matches must NOT falsely pass."""
    canonical = "key"
    assert check_answer("donkey", canonical) is False
    assert check_answer("keyboard", canonical) is False
    assert check_answer("turkey", canonical) is False
    assert check_answer("key", canonical) is True


def test_check_answer_empty_guess():
    """Empty or whitespace-only guess should fail."""
    assert check_answer("", "silver key") is False
    assert check_answer("   ", "silver key") is False


# ── Pydantic Schema Validation Tests ─────────────────────────────────────────
def test_curse_case_schema_valid():
    """Valid dictionary should parse into a CurseCase object."""
    valid_data = {
        "case_title": "The Curse of the Mirror",
        "haunted_object": "Antique hand mirror",
        "curse_description": "Whispers follow whoever peers into the glass.",
        "short_backstory": "Crafted in 1888 for a Parisian opera singer.",
        "puzzle_question": "What secret herb breaks the looking glass bind?",
        "initial_clue": "It grows near gravestones with golden petals.",
        "canonical_solution": "marigold",
        "accepted_aliases": ["cempasuchil"],
        "hint_1": "It is central to Día de los Muertos altars.",
        "hint_2": "Known in folklore as the flower of the dead, bright orange.",
        "success_explanation": "The glass shatters quietly and the spirit is released.",
    }
    case = CurseCase.model_validate(valid_data)
    assert case.case_title == "The Curse of the Mirror"
    assert case.canonical_solution == "marigold"
    assert "cempasuchil" in case.accepted_aliases


def test_curse_case_schema_missing_fields():
    """Missing required fields must raise a ValidationError."""
    invalid_data = {
        "case_title": "Incomplete Case",
        "haunted_object": "Broken locket",
    }
    with pytest.raises(ValidationError):
        CurseCase.model_validate(invalid_data)


# ── Solution Leak Detection Tests ─────────────────────────────────────────────
def test_detect_solution_leakage_detected():
    """Should detect when the secret answer appears in the visible puzzle text."""
    leaky_case = CurseCase(
        case_title="The Curse of the Marigold Garden",  # Leaks "marigold"
        haunted_object="A bronze vase",
        curse_description="The flowers wilt each night.",
        short_backstory="Placed upon an altar.",
        puzzle_question="Which flower must be burned?",
        initial_clue="A bright orange bloom.",
        canonical_solution="marigold",
        accepted_aliases=[],
        hint_1="Think of autumn.",
        hint_2="Known as cempasuchil.",
        success_explanation="The curse breaks.",
    )
    assert detect_solution_leakage(leaky_case) is True


def test_detect_solution_leakage_clean():
    """Clean puzzle without solution words should pass leak check."""
    clean_case = CurseCase(
        case_title="The Obsidian Hourglass",
        haunted_object="An antique sand glass",
        curse_description="Time loops backward every midnight.",
        short_backstory="Forged by an alchemist who feared death.",
        puzzle_question="What mineral must be cast into the upper chamber to freeze the grains?",
        initial_clue="An ancient white crystal used to preserve memories and ward off evil.",
        canonical_solution="salt",
        accepted_aliases=["sea salt", "rock salt"],
        hint_1="Found on dining tables and ocean tides.",
        hint_2="Common table seasoning that wards witches.",
        success_explanation="The sand turns to dust and the timeline restores.",
    )
    assert detect_solution_leakage(clean_case) is False


# ── Mock AI Puzzle Generation Tests ──────────────────────────────────────────
def test_generate_curse_puzzle_success():
    """Test generating a puzzle with valid mock model output."""
    mock_case_json = json.dumps({
        "case_title": "The Wailing Violin",
        "haunted_object": "An old violin",
        "curse_description": "Plays mournful melodies when no one is holding the bow.",
        "short_backstory": "Left in an abandoned conservatory after the 1906 quake.",
        "puzzle_question": "What metal must be wrapped around the fourth string?",
        "initial_clue": "The pale metal of mirrors and moonlight.",
        "canonical_solution": "silver",
        "accepted_aliases": ["silver wire"],
        "hint_1": "Used for purifying werewolf curses.",
        "hint_2": "Chemical symbol Ag.",
        "success_explanation": "The violin plays a soft chord and falls permanently silent.",
    })

    mock_provider = MagicMock(spec=AIProvider)
    mock_provider.generate.return_value = AIResponse(
        content=mock_case_json,
        model="qwen2.5:3b",
        provider="ollama",
        success=True,
    )

    case, err = generate_curse_puzzle(mock_provider, "An old violin", "qwen2.5:3b")
    assert err is None
    assert case is not None
    assert case.canonical_solution == "silver"
    assert case.case_title == "The Wailing Violin"


def test_generate_curse_puzzle_retry_on_leak():
    """Test retry logic when the first generated puzzle leaks the solution."""
    leaky_json = json.dumps({
        "case_title": "The Silver Bell of Despair",  # Leaks "silver"
        "haunted_object": "A silver bell",
        "curse_description": "Rings constantly.",
        "short_backstory": "Lost in 1900.",
        "puzzle_question": "What metal is it made of?",
        "initial_clue": "Silver shine.",
        "canonical_solution": "silver",
        "accepted_aliases": [],
        "hint_1": "Hint 1",
        "hint_2": "Hint 2",
        "success_explanation": "Saved.",
    })

    clean_json = json.dumps({
        "case_title": "The Bell of Despair",  # Fixed!
        "haunted_object": "An antique bell",
        "curse_description": "Rings constantly in the dead of night.",
        "short_backstory": "Lost in 1900.",
        "puzzle_question": "What moonlight alloy silences the clapper?",
        "initial_clue": "Tarnishes over time, loved by silversmiths.",
        "canonical_solution": "silver",
        "accepted_aliases": [],
        "hint_1": "Hint 1",
        "hint_2": "Hint 2",
        "success_explanation": "Saved.",
    })

    mock_provider = MagicMock(spec=AIProvider)
    mock_provider.generate.side_effect = [
        AIResponse(content=leaky_json, model="qwen2.5:3b", provider="ollama", success=True),
        AIResponse(content=clean_json, model="qwen2.5:3b", provider="ollama", success=True),
    ]

    case, err = generate_curse_puzzle(mock_provider, "An antique bell", "qwen2.5:3b", max_retries=2)
    assert err is None
    assert case is not None
    assert case.case_title == "The Bell of Despair"


# ── Storage Integration Tests ─────────────────────────────────────────────────
def test_storage_curse_cases():
    """Verify storing, updating, and retrieving curse cases."""
    case_data = {
        "case_title": "The Spectral Locket",
        "haunted_object": "Gold Locket",
        "canonical_solution": "rose",
    }
    save_curse_case(
        case_id="case-101",
        haunted_object="Gold Locket",
        case_title="The Spectral Locket",
        status="active",
        attempts_used=1,
        case_data=case_data,
    )

    cases = get_recent_curse_cases(limit=5)
    assert len(cases) == 1
    assert cases[0]["case_id"] == "case-101"
    assert cases[0]["status"] == "active"

    # Update status to solved
    update_curse_status("case-101", "solved", attempts_used=2)
    updated_cases = get_recent_curse_cases(limit=5)
    assert updated_cases[0]["status"] == "solved"
    assert updated_cases[0]["attempts_used"] == 2
