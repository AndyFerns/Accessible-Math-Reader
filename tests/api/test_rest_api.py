# ============================================================================
# tests/api/test_rest_api.py — REST API endpoint tests (/api/v1/*)
# ============================================================================
"""
Tests for the API Blueprint mounted by server.py:
  POST /api/v1/speech
  POST /api/v1/braille
  POST /api/v1/structure
  GET  /health
  GET  /readiness

Uses Flask test client with auth disabled (default).
"""

import json
from unittest.mock import patch, MagicMock

import pytest

from accessible_math_reader.server import create_app


@pytest.fixture()
def api_client():
    """Test client from the production server factory."""
    # Disable auth/rate limiting via env vars for testing
    with patch.dict("os.environ", {
        "AMR_ENABLE_AUTH": "false",
        "AMR_ENABLE_RATE_LIMIT": "false",
    }):
        app = create_app()
        app.config["TESTING"] = True
        with app.test_client() as c:
            yield c


def _post_json(client, path, data):
    """Helper: POST JSON and return response."""
    return client.post(
        path,
        data=json.dumps(data),
        content_type="application/json",
    )


# ══════════════════════════════════════════════════════════════════════════
# Infrastructure routes
# ══════════════════════════════════════════════════════════════════════════


class TestHealthEndpoint:
    def test_returns_200(self, api_client):
        resp = api_client.get("/health")
        assert resp.status_code == 200

    def test_json_status_healthy(self, api_client):
        data = api_client.get("/health").get_json()
        assert data["status"] == "healthy"

    def test_has_timestamp(self, api_client):
        data = api_client.get("/health").get_json()
        assert "timestamp" in data


class TestReadinessEndpoint:
    def test_returns_200(self, api_client):
        resp = api_client.get("/readiness")
        assert resp.status_code == 200

    def test_status_ready(self, api_client):
        data = api_client.get("/readiness").get_json()
        assert data["status"] == "ready"


# ══════════════════════════════════════════════════════════════════════════
# POST /api/v1/speech
# ══════════════════════════════════════════════════════════════════════════


class TestSpeechAPI:
    def test_valid_latex(self, api_client):
        resp = _post_json(api_client, "/api/v1/speech", {
            "input": r"\frac{a}{b}"
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "speech" in data
        assert isinstance(data["speech"], str)
        assert len(data["speech"]) > 0

    def test_speech_contains_over(self, api_client):
        data = _post_json(api_client, "/api/v1/speech", {
            "input": r"\frac{a}{b}"
        }).get_json()
        assert "over" in data["speech"].lower()

    def test_echoes_input(self, api_client):
        data = _post_json(api_client, "/api/v1/speech", {
            "input": "x+y"
        }).get_json()
        assert "input" in data

    def test_missing_input_returns_400(self, api_client):
        resp = _post_json(api_client, "/api/v1/speech", {})
        assert resp.status_code == 400

    def test_null_body_returns_400(self, api_client):
        resp = api_client.post(
            "/api/v1/speech",
            data="not json",
            content_type="application/json",
        )
        assert resp.status_code in (400, 422)


# ══════════════════════════════════════════════════════════════════════════
# POST /api/v1/braille
# ══════════════════════════════════════════════════════════════════════════


class TestBrailleAPI:
    def test_valid_latex(self, api_client):
        resp = _post_json(api_client, "/api/v1/braille", {
            "input": r"\frac{a}{b}"
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "braille" in data
        assert len(data["braille"]) > 0

    def test_notation_field(self, api_client):
        data = _post_json(api_client, "/api/v1/braille", {
            "input": "x", "notation": "nemeth"
        }).get_json()
        assert data.get("notation") == "nemeth"

    def test_missing_input_returns_400(self, api_client):
        resp = _post_json(api_client, "/api/v1/braille", {})
        assert resp.status_code == 400


# ══════════════════════════════════════════════════════════════════════════
# POST /api/v1/structure
# ══════════════════════════════════════════════════════════════════════════


class TestStructureAPI:
    def test_valid_input_returns_tree(self, api_client):
        resp = _post_json(api_client, "/api/v1/structure", {
            "input": r"\frac{a}{b}"
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "structure" in data
        assert isinstance(data["structure"], dict)

    def test_tree_has_type(self, api_client):
        data = _post_json(api_client, "/api/v1/structure", {
            "input": "x"
        }).get_json()
        assert "type" in data["structure"]

    def test_missing_input_returns_400(self, api_client):
        resp = _post_json(api_client, "/api/v1/structure", {})
        assert resp.status_code == 400
