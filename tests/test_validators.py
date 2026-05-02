"""Unit tests for input validators."""
import pytest
from fastapi import HTTPException
from app.utils.validators import (
    validate_query, validate_name,
    validate_pincode, validate_state, validate_language
)


class TestQueryValidator:
    def test_valid_query(self) -> None:
        assert validate_query("What is voter ID?") == "What is voter ID?"

    def test_empty_raises(self) -> None:
        with pytest.raises(HTTPException) as exc:
            validate_query("")
        assert exc.value.status_code == 400

    def test_too_long_raises(self) -> None:
        with pytest.raises(HTTPException):
            validate_query("x" * 501)

    def test_xss_sanitized(self) -> None:
        result = validate_query("Hello <script>")
        assert "<script>" not in result


class TestPincodeValidator:
    def test_valid_pincode(self) -> None:
        assert validate_pincode("110001") == "110001"

    def test_short_pincode_raises(self) -> None:
        with pytest.raises(HTTPException):
            validate_pincode("1234")

    def test_letters_raise(self) -> None:
        with pytest.raises(HTTPException):
            validate_pincode("ABCDEF")


class TestStateValidator:
    def test_valid_state(self) -> None:
        assert validate_state("Delhi") == "Delhi"

    def test_invalid_state_raises(self) -> None:
        with pytest.raises(HTTPException):
            validate_state("NotAState")


class TestLanguageValidator:
    def test_english_valid(self) -> None:
        assert validate_language("en") == "en"

    def test_hindi_valid(self) -> None:
        assert validate_language("hi") == "hi"

    def test_french_raises(self) -> None:
        with pytest.raises(HTTPException):
            validate_language("fr")
