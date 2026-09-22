"""
ScrapSense AI - Test Fixtures
"""
import sys
import os
import pytest

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["DISABLE_TORCH"] = "true"
os.environ["ADMIN_LOGIN"] = "admin"
os.environ["ADMIN_PASSWORD"] = "admin123"

from fastapi.testclient import TestClient
from main import app
from auth import create_access_token


@pytest.fixture
def client():
    """FastAPI TestClient for API testing."""
    return TestClient(app)


@pytest.fixture
def admin_token():
    """Pre-generated admin JWT token for authenticated requests."""
    return create_access_token({"sub": "admin", "role": "admin", "name": "Administrator"})


@pytest.fixture
def admin_headers(admin_token):
    """Authorization headers with admin JWT token."""
    return {"Authorization": f"Bearer {admin_token}"}
