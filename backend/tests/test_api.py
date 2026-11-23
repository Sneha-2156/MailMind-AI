"""API Integration Tests using FastAPI TestClient."""

import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "ok"]
    assert "MailMind" in data["app"]


def test_dev_login(client: TestClient):
    response = client.post("/api/v1/auth/dev-login")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "demo@mailmind.ai"


def test_unauthorized_access(client: TestClient):
    response = client.get("/api/v1/emails")
    assert response.status_code == 401
