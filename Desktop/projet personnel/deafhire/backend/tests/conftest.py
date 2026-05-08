"""
Shared pytest fixtures for DeafHire backend tests.
Uses an in-memory SQLite DB so tests never touch deafhire.db.
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure the backend package is importable from the tests/ subdirectory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Point database module to an in-memory DB before importing app
os.environ.setdefault("DATABASE_URL", ":memory:")

import database as db_module


@pytest.fixture(scope="session", autouse=True)
def in_memory_db(tmp_path_factory):
    """Replace the DB file with a fresh in-memory database for the test run."""
    tmp = tmp_path_factory.mktemp("db")
    db_path = str(tmp / "test.db")
    db_module.DB_PATH = db_path
    db_module.init_db()


@pytest.fixture(scope="session")
def client(in_memory_db):
    from main import app
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


@pytest.fixture()
def auth_headers(client):
    """Register a test user and return JWT auth headers."""
    client.post("/auth/register", json={
        "email": "test@deafhire.test",
        "password": "TestPass123!",
        "full_name": "Test User",
    })
    resp = client.post("/auth/login", data={
        "username": "test@deafhire.test",
        "password": "TestPass123!",
    })
    token = resp.json().get("access_token", "")
    return {"Authorization": f"Bearer {token}"}
