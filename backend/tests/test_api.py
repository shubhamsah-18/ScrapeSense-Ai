"""
ScrapSense AI - API Unit Tests
================================
Tests for all major API endpoints.
Run with: cd backend && python -m pytest tests/ -v
"""
import pytest
from auth import create_access_token
from seed_db import seed_database


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
        """GET /dealers should return dealer directory with matching total and count."""
        resp = client.get("/dealers")
        assert resp.status_code == 200
        data = resp.json()
        assert "dealers" in data
        assert "total" in data
        assert "count" in data
        assert data["total"] == data["count"]
        assert len(data["dealers"]) == data["total"]

    def test_get_dealers_with_category_filter(self, client):
        """GET /dealers?category=... should filter dealers and preserve total == count."""
        resp = client.get("/dealers?category=E-Waste")
        assert resp.status_code == 200
        data = resp.json()
        assert "dealers" in data
        assert "total" in data
        assert "count" in data
        assert data["total"] == data["count"]
        assert len(data["dealers"]) == data["total"]
        assert data["total"] > 0
        for dealer in data["dealers"]:
            dealer_types = [t.lower() for t in dealer.get("types", dealer.get("categories", []))]
            assert any("e-waste" in t for t in dealer_types)


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


class TestPhase2SecurityAndRBAC:
    """Regression tests for Phase 2 authorization, authentication, and RBAC."""

    def test_post_listings_no_token(self, client):
        """POST /listings without token should return 401."""
        resp = client.post("/listings", json={
            "item": "Copper Wire",
            "category": "Metals",
            "quantity": 10,
            "unit": "kg",
            "min_price": 400,
            "max_price": 500
        })
        assert resp.status_code == 401

    def test_patch_listings_no_token(self, client):
        """PATCH /listings/{id} without token should return 401."""
        resp = client.patch("/listings/65f000000000000000000001", json={
            "item": "Updated Scrap Copper"
        })
        assert resp.status_code == 401

    def test_delete_listings_no_token(self, client):
        """DELETE /listings/{id} without token should return 401."""
        resp = client.delete("/listings/65f000000000000000000001")
        assert resp.status_code == 401

    def test_post_approval_requests_no_token(self, client):
        """POST /approval-requests without token should return 401."""
        resp = client.post("/approval-requests", json={
            "listing_id": "65f000000000000000000001",
            "buyer_name": "Test Buyer",
            "offered_price": 450,
            "buyer_decision": "accepted"
        })
        assert resp.status_code == 401

    def test_get_receipt_no_token(self, client):
        """GET receipt endpoints without token should return 401."""
        resp1 = client.get("/orders/65f000000000000000000001/receipt")
        assert resp1.status_code == 401
        resp2 = client.get("/payments/receipt/65f000000000000000000001")
        assert resp2.status_code == 401

    def test_post_listings_wrong_role(self, client):
        """POST /listings with buyer-role token should return 403 Forbidden."""
        buyer_token = create_access_token({"sub": "buyer@test.com", "role": "buyer", "email": "buyer@test.com"})
        resp = client.post(
            "/listings",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={
                "item": "Copper Wire",
                "category": "Metals",
                "quantity": 10,
                "unit": "kg",
                "min_price": 400,
                "max_price": 500
            }
        )
        assert resp.status_code == 403
        assert "Access forbidden" in resp.json().get("detail", "") or "role" in resp.json().get("detail", "").lower()

    def test_post_approval_requests_wrong_role(self, client):
        """POST /approval-requests with seller-role token should return 403 Forbidden."""
        seller_token = create_access_token({"sub": "seller@test.com", "role": "seller", "email": "seller@test.com"})
        resp = client.post(
            "/approval-requests",
            headers={"Authorization": f"Bearer {seller_token}"},
            json={
                "listing_id": "65f000000000000000000001",
                "buyer_name": "Test Seller Attempting Buy",
                "offered_price": 450,
                "buyer_decision": "accepted"
            }
        )
        assert resp.status_code == 403
        assert "Access forbidden" in resp.json().get("detail", "") or "role" in resp.json().get("detail", "").lower()


class TestSeedIfEmptyMode:
    """Tests for seed-if-empty database initialization."""

    def test_seed_if_empty_skips_when_collections_contain_data(self):
        """With stubbed collections containing documents, seed-if-empty must not delete or insert."""
        class StubCollection:
            def __init__(self, doc_count=1):
                self._count = doc_count
                self.delete_calls = []
                self.insert_calls = []
                self.indexes = []

            def count_documents(self, filter_query=None):
                return self._count

            def estimated_document_count(self):
                return self._count

            def delete_many(self, filter_query):
                self.delete_calls.append(filter_query)

            def insert_many(self, docs):
                self.insert_calls.append(docs)

            def insert_one(self, doc):
                self.insert_calls.append(doc)

            def create_index(self, keys, **kwargs):
                self.indexes.append((keys, kwargs))

            def update_one(self, filter_query, update_query, **kwargs):
                pass

        class StubDatabase:
            def __init__(self):
                self.collections = {
                    "categories": StubCollection(doc_count=15),
                    "dealers": StubCollection(doc_count=10),
                    "users": StubCollection(doc_count=2),
                    "listings": StubCollection(doc_count=5),
                    "orders": StubCollection(doc_count=4),
                    "analytics": StubCollection(doc_count=1),
                }

            def __getitem__(self, name):
                if name not in self.collections:
                    self.collections[name] = StubCollection(doc_count=1)
                return self.collections[name]

            def __getattr__(self, name):
                return self[name]

        stub_db = StubDatabase()
        seed_database(seed_if_empty=True, db=stub_db)

        # Assert no deletes and no inserts occurred on the non-empty collections
        for col_name, col in stub_db.collections.items():
            assert len(col.delete_calls) == 0, f"Collection '{col_name}' had unexpected delete calls: {col.delete_calls}"
            assert len(col.insert_calls) == 0, f"Collection '{col_name}' had unexpected insert calls: {col.insert_calls}"


class TestForgotPasswordAndReset:
    """Tests for forgot password, OTP verification, password reset, and user reset."""

    def test_forgot_password_invalid_email(self, client):
        resp = client.post("/auth/forgot-password", json={"email": "notanemail"})
        assert resp.status_code == 422

    def test_forgot_password_user_not_found(self, client):
        resp = client.post("/auth/forgot-password", json={"email": "nonexistentuser999@example.com"})
        assert resp.status_code == 404

    def test_forgot_password_and_reset_flow(self, client):
        # 1. Request reset for demo seller apex.metals@scrapsense.org
        email = "apex.metals@scrapsense.org"
        forgot_resp = client.post("/auth/forgot-password", json={"email": email, "role": "seller"})
        assert forgot_resp.status_code == 200
        data = forgot_resp.json()
        assert data["status"] == "success"
        dev_otp = data.get("dev_otp")
        assert dev_otp is not None
        assert len(dev_otp) == 6

        # 2. Attempt reset with weak password
        weak_resp = client.post("/auth/reset-password", json={
            "email": email,
            "otp": dev_otp,
            "new_password": "short"
        })
        assert weak_resp.status_code == 422

        # 3. Attempt reset with incorrect OTP
        wrong_otp_resp = client.post("/auth/reset-password", json={
            "email": email,
            "otp": "000000",
            "new_password": "NewStrongPassword123!"
        })
        assert wrong_otp_resp.status_code == 401

        # 4. Successful reset with valid OTP and strong password
        new_pwd = "ApexNewPassword2026!"
        reset_resp = client.post("/auth/reset-password", json={
            "email": email,
            "otp": dev_otp,
            "new_password": new_pwd
        })
        assert reset_resp.status_code == 200
        assert reset_resp.json()["status"] == "success"

        # 5. Verify login works with new password
        login_resp = client.post("/auth/login", json={
            "email": email,
            "password": new_pwd,
            "role": "seller"
        })
        assert login_resp.status_code == 200
        assert login_resp.json()["email"] == email

    def test_admin_reset_users(self, client, admin_headers):
        # Without token -> 401
        resp_unauth = client.post("/admin/reset-users")
        assert resp_unauth.status_code == 401

        # With admin token -> 200
        resp_auth = client.post("/admin/reset-users", headers=admin_headers)
        assert resp_auth.status_code == 200
        data = resp_auth.json()
        assert data["status"] == "success"
        assert data["count"] >= 8

