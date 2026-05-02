"""
Module: test_validators.py
Purpose: Comprehensive unit tests for all input validator functions.
Author: Chunav Mitra Team
Version: 2.0.0
"""

import pytest
from fastapi import HTTPException

from app.utils.validators import (
    validate_language,
    validate_name,
    validate_pincode,
    validate_query,
    validate_state,
    validate_topic,
)


class TestQueryValidator:
    """Tests for validate_query."""

    def test_valid_english_query(self) -> None:
        """Standard English query should pass unchanged."""
        assert validate_query("What is voter ID?") == "What is voter ID?"

    def test_valid_hindi_query(self) -> None:
        """Hindi query should pass with length > 0."""
        result = validate_query("Voter list mein naam hai?")
        assert len(result) > 0

    def test_empty_string_raises_400(self) -> None:
        """Empty string must raise HTTP 400."""
        with pytest.raises(HTTPException) as exc:
            validate_query("")
        assert exc.value.status_code == 400

    def test_whitespace_only_raises_400(self) -> None:
        """Whitespace-only string must raise HTTP 400."""
        with pytest.raises(HTTPException) as exc:
            validate_query("   ")
        assert exc.value.status_code == 400

    def test_501_chars_raises_400(self) -> None:
        """String longer than 500 chars must raise HTTP 400."""
        with pytest.raises(HTTPException) as exc:
            validate_query("a" * 501)
        assert exc.value.status_code == 400

    def test_500_chars_passes(self) -> None:
        """Exactly 500 characters must pass."""
        result = validate_query("a" * 500)
        assert len(result) == 500

    def test_xss_script_tag_removed(self) -> None:
        """HTML script tags must be stripped from the query."""
        result = validate_query("Hello <script>alert(1)</script>")
        assert "<script>" not in result

    def test_sql_injection_sanitized(self) -> None:
        """SQL injection payload must not raise but result is returned."""
        result = validate_query("SELECT * FROM users; DROP TABLE")
        assert result is not None

    def test_angle_brackets_removed(self) -> None:
        """Angle brackets must be removed from query."""
        result = validate_query("test <b>bold</b>")
        assert "<" not in result and ">" not in result


class TestNameValidator:
    """Tests for validate_name."""

    def test_valid_latin_name(self) -> None:
        """Standard Latin name should pass unchanged."""
        assert validate_name("Rahul Sharma") == "Rahul Sharma"

    def test_single_char_raises(self) -> None:
        """Single character name must raise HTTP 400."""
        with pytest.raises(HTTPException) as exc:
            validate_name("A")
        assert exc.value.status_code == 400

    def test_empty_raises(self) -> None:
        """Empty string must raise HTTP 400."""
        with pytest.raises(HTTPException):
            validate_name("")

    def test_101_chars_raises(self) -> None:
        """Name longer than 100 chars must raise HTTP 400."""
        with pytest.raises(HTTPException):
            validate_name("A" * 101)

    def test_hindi_name_valid(self) -> None:
        """Hindi Devanagari name must be accepted."""
        result = validate_name("राहुल शर्मा")
        assert len(result) > 0

    def test_name_with_hyphen(self) -> None:
        """Hyphenated name must be accepted."""
        result = validate_name("Priya-Singh")
        assert "Priya" in result

    def test_special_chars_stripped(self) -> None:
        """Special characters outside allowed set must be stripped."""
        result = validate_name("Rahul@123")
        assert "@" not in result and "123" not in result


class TestPincodeValidator:
    """Tests for validate_pincode."""

    def test_valid_delhi_pincode(self) -> None:
        """Delhi pincode 110001 must pass unchanged."""
        assert validate_pincode("110001") == "110001"

    def test_valid_mumbai_pincode(self) -> None:
        """Mumbai pincode 400001 must pass unchanged."""
        assert validate_pincode("400001") == "400001"

    def test_5_digit_raises(self) -> None:
        """Five-digit pincode must raise HTTP 400."""
        with pytest.raises(HTTPException) as exc:
            validate_pincode("12345")
        assert exc.value.status_code == 400

    def test_7_digit_raises(self) -> None:
        """Seven-digit pincode must raise HTTP 400."""
        with pytest.raises(HTTPException):
            validate_pincode("1234567")

    def test_letters_raise(self) -> None:
        """Alphabetic pincode must raise HTTP 400."""
        with pytest.raises(HTTPException):
            validate_pincode("ABCDEF")

    def test_mixed_raises(self) -> None:
        """Alphanumeric pincode must raise HTTP 400."""
        with pytest.raises(HTTPException):
            validate_pincode("1100A1")

    def test_with_spaces_raises(self) -> None:
        """Pincode with spaces must raise HTTP 400."""
        with pytest.raises(HTTPException):
            validate_pincode("110 001")


class TestStateValidator:
    """Tests for validate_state."""

    def test_delhi_valid(self) -> None:
        """Delhi must be a valid state."""
        assert validate_state("Delhi") == "Delhi"

    def test_maharashtra_valid(self) -> None:
        """Maharashtra must be a valid state."""
        assert validate_state("Maharashtra") == "Maharashtra"

    def test_uttar_pradesh_valid(self) -> None:
        """Uttar Pradesh must be a valid state."""
        assert validate_state("Uttar Pradesh") == "Uttar Pradesh"

    def test_invalid_state_raises(self) -> None:
        """Unrecognised state name must raise HTTP 400."""
        with pytest.raises(HTTPException) as exc:
            validate_state("NotAState")
        assert exc.value.status_code == 400

    def test_lowercase_raises(self) -> None:
        """Lowercase state name must raise HTTP 400 (exact match required)."""
        with pytest.raises(HTTPException):
            validate_state("delhi")

    def test_all_states_length(self) -> None:
        """INDIAN_STATES must have at least 36 entries."""
        from app.utils.constants import INDIAN_STATES
        assert len(INDIAN_STATES) >= 36


class TestLanguageValidator:
    """Tests for validate_language."""

    def test_english_valid(self) -> None:
        """'en' must be accepted and returned unchanged."""
        assert validate_language("en") == "en"

    def test_hindi_valid(self) -> None:
        """'hi' must be accepted and returned unchanged."""
        assert validate_language("hi") == "hi"

    def test_french_raises(self) -> None:
        """Unsupported language code must raise HTTP 400."""
        with pytest.raises(HTTPException) as exc:
            validate_language("fr")
        assert exc.value.status_code == 400

    def test_empty_raises(self) -> None:
        """Empty language string must raise HTTP 400."""
        with pytest.raises(HTTPException):
            validate_language("")

    def test_none_returns_default(self) -> None:
        """None must return the default language 'en'."""
        assert validate_language(None) == "en"


class TestTopicValidator:
    """Tests for validate_topic."""

    def test_evm_canonical(self) -> None:
        """Canonical 'EVM' must pass and return 'EVM'."""
        assert validate_topic("EVM") == "EVM"

    def test_nota_canonical(self) -> None:
        """Canonical 'NOTA' must pass and return 'NOTA'."""
        assert validate_topic("NOTA") == "NOTA"

    def test_evm_lowercase_alias(self) -> None:
        """Lowercase alias 'evm' must resolve to canonical 'EVM'."""
        assert validate_topic("evm") == "EVM"

    def test_nota_lowercase_alias(self) -> None:
        """Lowercase alias 'nota' must resolve to canonical 'NOTA'."""
        assert validate_topic("nota") == "NOTA"

    def test_booth_alias(self) -> None:
        """'booth' alias must resolve to canonical 'Booth'."""
        assert validate_topic("booth") == "Booth"

    def test_counting_alias(self) -> None:
        """'counting' alias must resolve to 'Vote Counting'."""
        assert validate_topic("counting") == "Vote Counting"

    def test_invalid_raises_400(self) -> None:
        """Unrecognised topic must raise HTTP 400."""
        with pytest.raises(HTTPException) as exc:
            validate_topic("INVALID")
        assert exc.value.status_code == 400

    def test_empty_raises_400(self) -> None:
        """Empty topic must raise HTTP 400."""
        with pytest.raises(HTTPException) as exc:
            validate_topic("")
        assert exc.value.status_code == 400
