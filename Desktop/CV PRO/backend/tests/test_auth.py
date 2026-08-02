import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"

def test_api_root():
    """Test API root endpoint"""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

def test_jobs_list():
    """Test jobs listing"""
    response = client.get("/api/v1/jobs/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_recommendations_list():
    """Test recommendations"""
    response = client.get("/api/v1/recommendations/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_applications_list():
    """Test applications list"""
    response = client.get("/api/v1/applications/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_analytics_dashboard():
    """Test analytics dashboard"""
    response = client.get("/api/v1/analytics/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "applications" in data
    assert "favorites" in data
    assert "searches" in data
