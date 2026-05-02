"""Integration tests for Chunav Mitra API routes."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_correct_schema(self):
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


class TestAskEndpoint:
    @patch("app.services.gemini_service.ask_gemini")
    def test_ask_returns_response(self, mock_gemini):
        mock_gemini.return_value = "Test shaadi response"
        response = client.post("/api/ask", json={"query": "What is voter ID?"})
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "session_id" in data
        assert "intent" in data

    def test_ask_empty_query_returns_400(self):
        response = client.post("/api/ask", json={"query": ""})
        assert response.status_code == 400

    def test_ask_too_long_query_returns_400(self):
        response = client.post("/api/ask", json={"query": "x" * 501})
        assert response.status_code == 400


class TestVoterEndpoint:
    def test_voter_check_valid_input(self):
        response = client.post("/api/check-voter", json={"name": "Rahul Sharma", "state": "Delhi"})
        assert response.status_code == 200
        data = response.json()
        assert "found" in data
        assert "message" in data

    def test_voter_check_missing_name(self):
        response = client.post("/api/check-voter", json={"name": "", "state": "Delhi"})
        assert response.status_code == 400


class TestBoothEndpoint:
    @patch("app.routes.booth.find_nearest_booth")
    def test_booth_finder_with_pincode(self, mock_find_nearest_booth):
        mock_find_nearest_booth.return_value = {
            "booth_name": "Test Booth",
            "address": "Test Address",
            "distance": "1.2 km",
            "maps_link": "https://maps.google.com",
            "lat": 28.6,
            "lng": 77.2,
        }
        response = client.post("/api/find-booth", json={"pincode": "110001"})
        assert response.status_code == 200

    def test_booth_finder_invalid_pincode(self):
        response = client.post("/api/find-booth", json={"pincode": "123"})
        assert response.status_code == 400

    def test_booth_finder_missing_input(self):
        response = client.post("/api/find-booth", json={})
        assert response.status_code == 400


class TestTimelineEndpoint:
    def test_timeline_returns_phases(self):
        response = client.get("/api/timeline")
        assert response.status_code == 200
        data = response.json()
        assert "phases" in data
        assert len(data["phases"]) > 0
        assert "current_phase" in data


class TestExplainEndpoint:
    @patch("app.services.gemini_service.ask_gemini")
    def test_explain_valid_topic(self, mock_gemini):
        mock_gemini.return_value = (
            '{"shaadi_analogy":"test","simple_explanation":"test","action_step":"test","fun_fact":"test"}'
        )
        response = client.post("/api/explain", json={"topic": "Model Code", "lang": "en"})
        assert response.status_code == 200

    def test_explain_local_topic_in_hindi(self):
        response = client.post("/api/explain", json={"topic": "Election Commission", "lang": "hi"})
        assert response.status_code == 200
        assert "topic" in response.json()

    @patch("app.services.gemini_service.ask_gemini")
    def test_explain_generated_topic(self, mock_gemini):
        mock_gemini.return_value = (
            '{"shaadi_analogy":"custom","simple_explanation":"custom","action_step":"custom","fun_fact":"custom"}'
        )
        response = client.post("/api/explain", json={"topic": "Custom Topic", "lang": "en"})
        assert response.status_code == 200


class TestStatsEndpoint:
    def test_stats_returns_schema(self):
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_queries" in data
        assert "languages_used" in data

    def test_stats_detailed_returns_schema(self):
        response = client.get("/api/stats/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "daily_breakdown" in data
        assert "hourly_distribution" in data


class TestTranslateEndpoint:
    @patch("app.routes.translate.translate_to")
    def test_translate_batch(self, mock_translate):
        mock_translate.side_effect = lambda text, target: f"{text}-{target}"
        response = client.post("/api/translate", json={"texts": ["Hello"], "target_lang": "hi"})
        assert response.status_code == 200
        assert response.json()["texts"][0] == "Hello-hi"


class TestTranscribeEndpoint:
    @patch("app.routes.transcribe.requests.post")
    def test_transcribe_success(self, mock_post):
        mock_post.return_value.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "spoken words"}]}}]
        }
        mock_post.return_value.raise_for_status.return_value = None
        with patch("app.routes.transcribe.GEMINI_API_KEY", "test-key"):
            response = client.post(
                "/api/transcribe",
                files={"audio": ("voice.webm", b"audio-bytes", "audio/webm")},
                data={"lang": "en"},
            )
        assert response.status_code == 200
        assert response.json()["text"] == "spoken words"
