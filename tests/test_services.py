"""Unit tests for Chunav Mitra services."""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.routes.explain import build_explain_response, build_generic_fallback, parse_json_response
from app.middleware.rate_limiter import RateLimitMiddleware, get_rate_limit_status
from app.services import firebase_service, gemini_service, maps_service, translate_service
from app.services.gemini_service import classify_intent
from app.services.translate_service import detect_language
from app.utils.cache import SimpleCache
from app.utils.validators import (
    validate_language,
    validate_name,
    validate_pincode,
    validate_query,
    validate_state,
    validate_topic,
)


class TestIntentClassifier:
    def test_voter_check_intent(self):
        result = classify_intent("How do I check voter list?")
        assert result["intent"] == "voter_check"
        assert result["confidence"] > 0.8

    def test_booth_finder_intent(self):
        result = classify_intent("Where is my polling booth?")
        assert result["intent"] == "booth_finder"

    def test_timeline_intent(self):
        result = classify_intent("When is the election date?")
        assert result["intent"] == "timeline"

    def test_hindi_voter_intent(self):
        result = classify_intent("Voter list mein naam kaise check karein?")
        assert result["intent"] == "voter_check"

    def test_general_intent(self):
        result = classify_intent("Hello there")
        assert result["intent"] == "general"


class TestTranslateService:
    def test_detect_language_defaults_for_empty_text(self):
        assert detect_language("") == "en"

    @patch("app.services.translate_service.GoogleTranslator")
    def test_translate_to_english(self, mock_translator):
        mock_translator.return_value.translate.return_value = "Hello"
        assert translate_service.translate_to_english("नमस्ते") == "Hello"

    @patch("app.services.translate_service.GoogleTranslator")
    def test_translate_to_hindi(self, mock_translator):
        mock_translator.return_value.translate.return_value = "नमस्ते"
        assert translate_service.translate_to_hindi("Hello") == "नमस्ते"

    @patch("app.services.translate_service.GoogleTranslator")
    def test_translate_to_generic(self, mock_translator):
        mock_translator.return_value.translate.return_value = "Hola"
        assert translate_service.translate_to("Hello", "es") == "Hola"

    @patch("app.services.translate_service.GoogleTranslator")
    def test_translate_to_fallback_on_error(self, mock_translator):
        mock_translator.return_value.translate.side_effect = RuntimeError("boom")
        assert translate_service.translate_to_hindi("Hello") == "Hello"

    def test_translate_to_invalid_inputs(self):
        with pytest.raises(ValueError):
            translate_service.detect_language(123)  # type: ignore[arg-type]
        with pytest.raises(ValueError):
            translate_service.translate_to(123, "hi")  # type: ignore[arg-type]
        with pytest.raises(ValueError):
            translate_service.translate_to("hello", "")


class TestCache:
    def test_cache_set_and_get(self):
        simple_cache = SimpleCache()
        key = simple_cache.make_key("timeline")
        simple_cache.set(key, {"ok": True}, ttl_seconds=60)
        assert simple_cache.get(key) == {"ok": True}

    def test_cache_clear_expired(self):
        simple_cache = SimpleCache()
        key = simple_cache.make_key("expired")
        simple_cache.set(key, "value", ttl_seconds=-1)
        simple_cache.clear_expired()
        assert simple_cache.get(key) is None


class TestFirebaseService:
    def test_mock_session_and_history(self):
        firebase_service.db = None
        session_id = firebase_service.create_session()
        firebase_service.save_message(session_id, "user", "Hello")
        history = firebase_service.get_history(session_id)
        assert history[-1]["parts"][0] == "Hello"

    def test_log_query_in_mock_mode(self):
        firebase_service.db = None
        session_id = firebase_service.create_session()
        firebase_service.log_query(session_id, "general", "en")
        assert any(item["session_id"] == session_id for item in firebase_service._mock_analytics)


class TestMapsService:
    @patch("app.services.maps_service._query_overpass")
    @patch("app.services.maps_service._resolve_coordinates_from_pincode")
    def test_find_nearest_booth_from_pincode(self, mock_resolve, mock_query):
        mock_resolve.return_value = (28.6, 77.2)
        mock_query.return_value = {
            "lat": 28.61,
            "lon": 77.21,
            "tags": {"name": "Test Booth", "addr:full": "Test Address"},
        }
        result = maps_service.find_nearest_booth(pincode="110001")
        assert result["booth_name"] == "Test Booth"

    def test_find_nearest_booth_requires_input(self):
        with pytest.raises(ValueError):
            maps_service.find_nearest_booth()

    def test_build_booth_from_element(self):
        result = maps_service._build_booth_from_element(
            28.6,
            77.2,
            {"lat": 28.61, "lon": 77.21, "tags": {"name": "Booth", "addr:full": "Addr"}},
            "Fallback",
        )
        assert result["booth_name"] == "Booth"

    @patch("app.services.maps_service._resolve_coordinates_from_pincode")
    def test_find_nearest_booth_unresolved_pincode(self, mock_resolve):
        mock_resolve.return_value = None
        result = maps_service.find_nearest_booth(pincode="110001")
        assert "error" in result

    @patch("app.services.maps_service.geolocator.reverse")
    @patch("app.services.maps_service._query_overpass")
    def test_find_nearest_booth_reverse_fallback(self, mock_query, mock_reverse):
        mock_query.side_effect = RuntimeError("down")
        mock_reverse.return_value = type("Location", (), {"address": "Fallback Address"})()
        result = maps_service.find_nearest_booth(lat=28.6, lng=77.2)
        assert result["address"] == "Fallback Address"


class TestGeminiService:
    def test_build_model_requires_name(self):
        with pytest.raises(ValueError):
            gemini_service.build_model("")

    def test_get_response_text(self):
        response = type("Response", (), {"text": " hello "})()
        assert gemini_service._get_response_text(response) == "hello"

    def test_quota_like_error(self):
        assert gemini_service._quota_like_error(Exception("429 quota exceeded")) is True

    @patch("app.services.gemini_service.genai.GenerativeModel")
    def test_summarize_history(self, mock_model):
        mock_instance = mock_model.return_value
        mock_instance.generate_content.return_value.text = "summary"
        history = [{"role": "user", "parts": ["hello"]}]
        assert gemini_service.summarize_history(history) == "summary"

    def test_ask_gemini_with_fallback_success(self):
        class FakeChat:
            def send_message(self, query):
                return type("Response", (), {"text": f"answer:{query}"})()

        class FakeModel:
            def start_chat(self, history):
                return FakeChat()

            def generate_content(self, query):
                return type("Response", (), {"text": f"answer:{query}"})()

        with patch("app.services.gemini_service.build_model", return_value=FakeModel()):
            assert gemini_service.ask_gemini_with_fallback("hello") == "answer:hello"

    def test_ask_gemini_returns_sanitized_error(self):
        with patch("app.services.gemini_service.ask_gemini_with_fallback", side_effect=RuntimeError("boom")):
            assert "technical issue" in gemini_service.ask_gemini("hello")

    @pytest.mark.asyncio
    async def test_ask_gemini_stream_success(self):
        class FakeChunk:
            def __init__(self, text):
                self.text = text

        class FakeModel:
            async def generate_content_async(self, query, stream=True):
                async def generator():
                    yield FakeChunk("hello")
                    yield FakeChunk(" world")

                return generator()

        with patch("app.services.gemini_service.build_model", return_value=FakeModel()):
            chunks = [chunk async for chunk in gemini_service.ask_gemini_stream("hello")]
            assert "".join(chunks) == "hello world"

    @pytest.mark.asyncio
    async def test_ask_gemini_stream_failure(self):
        class FakeModel:
            async def generate_content_async(self, query, stream=True):
                raise RuntimeError("boom")

        with patch("app.services.gemini_service.build_model", return_value=FakeModel()):
            chunks = [chunk async for chunk in gemini_service.ask_gemini_stream("hello")]
            assert "technical issue" in chunks[0]


class TestExplainHelpers:
    def test_parse_json_response_direct(self):
        parsed = parse_json_response('{"shaadi_analogy":"a"}')
        assert parsed == {"shaadi_analogy": "a"}

    def test_parse_json_response_markdown(self):
        parsed = parse_json_response('```json\n{"shaadi_analogy":"a"}\n```')
        assert parsed == {"shaadi_analogy": "a"}

    def test_build_explain_response(self):
        response = build_explain_response(
            "EVM",
            "en",
            {
                "shaadi_analogy": "a",
                "simple_explanation": "b",
                "action_step": "c",
                "fun_fact": "d",
            },
        )
        assert response.topic == "EVM"

    def test_build_generic_fallback(self):
        fallback = build_generic_fallback("Topic")
        assert "Topic" in fallback["shaadi_analogy"]

    @patch("app.routes.explain.translate_to_hindi")
    def test_build_explain_response_hindi_translation(self, mock_translate):
        mock_translate.side_effect = lambda value: f"hi:{value}"
        response = build_explain_response(
            "Topic",
            "hi",
            {
                "shaadi_analogy": "analogy",
                "simple_explanation": "simple",
                "action_step": "step",
                "fun_fact": "fact",
            },
        )
        assert response.shaadi_analogy.startswith("hi:")


class TestRateLimitHelpers:
    def test_rate_limit_status(self):
        status = get_rate_limit_status("127.0.0.1")
        assert "limit" in status

    def test_get_client_ip(self):
        middleware = RateLimitMiddleware(app=None)  # type: ignore[arg-type]
        request = type(
            "Request",
            (),
            {"headers": {"X-Forwarded-For": "1.2.3.4"}, "client": type("Client", (), {"host": "9.9.9.9"})()},
        )()
        assert middleware._get_client_ip(request) == "1.2.3.4"

    def test_check_rate_limit(self):
        middleware = RateLimitMiddleware(app=None)  # type: ignore[arg-type]
        allowed, retry_after = middleware._check_rate_limit("test-ip")
        assert allowed is True
        assert retry_after == 0


class TestValidators:
    def test_valid_query_passes(self):
        result = validate_query("What is voter ID?")
        assert result == "What is voter ID?"

    def test_empty_query_raises(self):
        with pytest.raises(HTTPException) as exc:
            validate_query("")
        assert exc.value.status_code == 400

    def test_long_query_raises(self):
        with pytest.raises(HTTPException):
            validate_query("x" * 501)

    def test_valid_pincode(self):
        result = validate_pincode("110001")
        assert result == "110001"

    def test_invalid_pincode_raises(self):
        with pytest.raises(HTTPException):
            validate_pincode("123")

    def test_validate_name(self):
        assert validate_name("Rahul Sharma") == "Rahul Sharma"

    def test_validate_state(self):
        assert validate_state("Delhi") == "Delhi"

    def test_validate_language(self):
        assert validate_language("hi") == "hi"

    def test_validate_topic(self):
        assert validate_topic("EVM") == "EVM"


class TestAskHelpers:
    def test_local_intent_response(self):
        from app.routes.ask import build_local_intent_response

        response = build_local_intent_response("timeline", "when is voting", "en")
        assert response is not None
