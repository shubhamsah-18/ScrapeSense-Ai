"""
ScrapSense AI - API Unit Tests
================================
Tests for all major API endpoints.
Run with: cd backend && python -m pytest tests/ -v
"""
import pytest


class TestHealthEndpoints:
    """Tests for health and status endpoints."""

    def test_root_returns_ok(self, client):
        """GET / should return service status."""
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "ScrapSense AI Backend"
        assert "version" in data
        assert "categories_count" in data

    def test_health_check(self, client):
        """GET /health should return healthy status."""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "model_status" in data
        assert "device" in data

    def test_network_info(self, client):
        """GET /network-info should return IP and port details."""
        resp = client.get("/network-info")
        assert resp.status_code == 200
        data = resp.json()
        assert "primary_ip" in data
        assert data["frontend_port"] == 5500
        assert data["backend_port"] == 8000


class TestCategoryEndpoints:
    """Tests for scrap category and pricing endpoints."""

    def test_get_categories(self, client):
        """GET /categories should return non-empty category list."""
        resp = client.get("/categories")
        assert resp.status_code == 200
        data = resp.json()
        assert "categories" in data
        assert len(data["categories"]) > 0
        first = data["categories"][0]
        assert "display_name" in first
        assert "category" in first
        assert "min_price" in first
        assert "max_price" in first

    def test_get_categories_with_city(self, client):
        """GET /categories?city=Mumbai should apply city price factor."""
        resp = client.get("/categories?city=Mumbai")
        assert resp.status_code == 200
        data = resp.json()
        assert data["city"] == "Mumbai"
        assert data["city_factor"] == 1.04

    def test_get_stats(self, client):
        """GET /stats should return platform statistics."""
        resp = client.get("/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_categories"] > 0
        assert "groups" in data
        assert "dealers_count" in data

    def test_get_dealers(self, client):
        """GET /dealers should return dealer directory."""
        resp = client.get("/dealers")
        assert resp.status_code == 200
        data = resp.json()
        assert "dealers" in data
        assert "total" in data


class TestCalculateEndpoint:
    """Tests for the resale value calculator."""

    def test_calculate_resale_basic(self, client):
        """POST /calculate should return payout estimates."""
        resp = client.post("/calculate", json={
            "category_key": "a computer motherboard or circuit board",
            "quantity": 5.0
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["quantity"] == 5.0
        assert data["min_payout"] > 0
        assert data["expected_payout"] > 0
        assert data["max_payout"] >= data["min_payout"]
        assert "eco_impact" in data

    def test_calculate_resale_by_display_name(self, client):
        """POST /calculate with display_name should match category."""
        resp = client.post("/calculate", json={
            "display_name": "Motherboard PCB",
            "quantity": 10.0
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["item_name"] == "Motherboard PCB"
        assert data["quantity"] == 10.0


class TestAIEndpoints:
    """Tests for AI service endpoints."""

    def test_ai_status(self, client):
        """GET /ai/status should return provider availability."""
        resp = client.get("/ai/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "providers" in data
        assert "default_provider" in data
        assert "openai" in data["providers"]
        assert "claude" in data["providers"]
        assert "gemini" in data["providers"]

    def test_ai_chat_returns_response(self, client):
        """POST /ai/chat should return an AI response (simulated or live)."""
        resp = client.post("/ai/chat", json={
            "message": "What is the current rate for copper wire?",
            "provider": "gemini",
            "history": []
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "response" in data
        assert len(data["response"]) > 0
        assert "provider" in data


class TestAuthEndpoints:
    """Tests for authentication endpoints."""

    def test_admin_login_success(self, client):
        """POST /auth/login should accept correct admin credentials."""
        resp = client.post("/auth/login", json={
            "email": "admin",
            "password": "admin123",
            "role": "admin"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] == "admin"
        assert "token" in data

    def test_admin_login_invalid(self, client):
        """POST /auth/login with wrong admin password should return 401."""
        resp = client.post("/auth/login", json={
            "email": "admin",
            "password": "wrongpassword",
            "role": "admin"
        })
        assert resp.status_code == 401

    def test_protected_endpoint_no_auth(self, client):
        """GET /admin/users without token should return 401."""
        resp = client.get("/admin/users")
        assert resp.status_code == 401


class TestPredictEndpoint:
    """Tests for the image classification endpoint."""

    def test_predict_rejects_non_image(self, client):
        """POST /predict with non-image file should return 400."""
        resp = client.post("/predict", files={
            "file": ("test.txt", b"not an image", "text/plain")
        })
        assert resp.status_code == 400
