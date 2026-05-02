"""Integration tests for all Chunav Mitra API routes."""
import pytest
from unittest.mock import patch


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_returns_200(self, client) -> None:
        """Health endpoint should return HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_schema(self, client) -> None:
        """Health endpoint should return correct JSON schema."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_root_returns_200(self, client) -> None:
        """Root endpoint should return HTTP 200."""
        response = client.get("/")
        assert response.status_code == 200


class TestAskEndpoint:
    """Tests for POST /api/ask chat endpoint."""

    def test_ask_valid_query(self, client, mock_gemini) -> None:
        """Valid query should return 200 with response."""
        response = client.post("/api/ask",
            json={"query": "What is a polling booth?"})
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "session_id" in data
        assert "intent" in data
        assert "detected_lang" in data

    def test_ask_empty_query_returns_400(self, client) -> None:
        """Empty query should return HTTP 400."""
        response = client.post("/api/ask", json={"query": ""})
        assert response.status_code == 400

    def test_ask_too_long_returns_400(self, client) -> None:
        """Query exceeding 500 chars should return HTTP 400."""
        response = client.post("/api/ask",
            json={"query": "x" * 501})
        assert response.status_code == 400

    def test_ask_hindi_query(self, client, mock_gemini) -> None:
        """Hindi queries should be accepted."""
        response = client.post("/api/ask",
            json={"query": "Voter list mein naam kaise check karein?"})
        assert response.status_code == 200

    def test_ask_with_session_id(self, client, mock_gemini) -> None:
        """Query with session_id should maintain context."""
        response = client.post("/api/ask",
            json={"query": "Hello", "session_id": "test-123"})
        assert response.status_code == 200
        assert response.json()["session_id"] == "test-123"


class TestVoterEndpoint:
    """Tests for POST /api/check-voter endpoint."""

    def test_voter_check_valid(self, client) -> None:
        """Valid voter check should return 200."""
        response = client.post("/api/check-voter",
            json={"name": "Rahul Sharma", "state": "Delhi"})
        assert response.status_code == 200
        data = response.json()
        assert "found" in data
        assert "message" in data

    def test_voter_check_empty_name(self, client) -> None:
        """Empty name should return 400."""
        response = client.post("/api/check-voter",
            json={"name": "", "state": "Delhi"})
        assert response.status_code == 400

    def test_voter_check_invalid_state(self, client) -> None:
        """Invalid state should return 400."""
        response = client.post("/api/check-voter",
            json={"name": "Test User", "state": "InvalidState"})
        assert response.status_code == 400

    def test_voter_check_response_has_shaadi_analogy(self, client) -> None:
        """Response message should contain shaadi analogy."""
        response = client.post("/api/check-voter",
            json={"name": "Priya Singh", "state": "Maharashtra"})
        data = response.json()
        assert len(data["message"]) > 10


class TestBoothEndpoint:
    """Tests for POST /api/find-booth endpoint."""

    def test_booth_with_pincode(self, client) -> None:
        """Valid pincode should trigger booth search."""
        with patch("app.services.maps_service.find_nearest_booth") as mock:
            mock.return_value = {
                "booth_name": "Govt School",
                "address": "Test Address, Delhi",
                "distance": "1.2 km",
                "maps_link": "https://maps.google.com",
                "lat": 28.6139, "lng": 77.2090
            }
            response = client.post("/api/find-booth",
                json={"pincode": "110001"})
            assert response.status_code == 200
            data = response.json()
            assert "booth_name" in data
            assert "maps_link" in data

    def test_booth_invalid_pincode(self, client) -> None:
        """Invalid pincode format should return 400."""
        response = client.post("/api/find-booth",
            json={"pincode": "123"})
        assert response.status_code == 400

    def test_booth_no_location_returns_400(self, client) -> None:
        """Missing both pincode and GPS should return 400."""
        response = client.post("/api/find-booth", json={})
        assert response.status_code == 400


class TestTimelineEndpoint:
    """Tests for GET /api/timeline endpoint."""

    def test_timeline_returns_200(self, client) -> None:
        """Timeline should return HTTP 200."""
        response = client.get("/api/timeline")
        assert response.status_code == 200

    def test_timeline_has_phases(self, client) -> None:
        """Timeline should contain phases array."""
        response = client.get("/api/timeline")
        data = response.json()
        assert "phases" in data
        assert isinstance(data["phases"], list)
        assert len(data["phases"]) > 0

    def test_timeline_phase_structure(self, client) -> None:
        """Each phase should have required fields."""
        response = client.get("/api/timeline")
        phase = response.json()["phases"][0]
        assert "phase" in phase
        assert "name" in phase
        assert "date" in phase
        assert "description" in phase

    def test_timeline_has_current_phase(self, client) -> None:
        """Timeline should indicate current phase."""
        response = client.get("/api/timeline")
        data = response.json()
        assert "current_phase" in data
        assert "days_remaining" in data


class TestExplainEndpoint:
    """Tests for POST /api/explain endpoint."""

    def test_explain_valid_topic(self, client, mock_gemini) -> None:
        """Valid topic should return explanation."""
        # EVM is in LOCAL_EXPLAINERS so it returns without calling gemini
        response = client.post("/api/explain",
            json={"topic": "EVM", "lang": "en"})
        assert response.status_code == 200

    def test_explain_invalid_topic(self, client) -> None:
        """Invalid topic should return 400."""
        response = client.post("/api/explain",
            json={"topic": "InvalidTopic", "lang": "en"})
        assert response.status_code == 400

    def test_explain_invalid_lang(self, client) -> None:
        """Invalid language (not in Literal schema) returns 422 from Pydantic."""
        response = client.post("/api/explain",
            json={"topic": "EVM", "lang": "fr"})
        # Pydantic rejects 'fr' at schema level → 422 Unprocessable Entity
        assert response.status_code == 422
