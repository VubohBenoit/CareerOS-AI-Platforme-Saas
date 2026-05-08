"""Authentication route tests."""

import pytest


REGISTER_PAYLOAD = {
    "email": "auth_test@deafhire.test",
    "password": "SecurePass999!",
    "full_name": "Auth Tester",
}


def test_register_new_user(client):
    resp = client.post("/auth/register", json=REGISTER_PAYLOAD)
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data.get("email") == REGISTER_PAYLOAD["email"]


def test_register_duplicate_email(client):
    client.post("/auth/register", json=REGISTER_PAYLOAD)
    resp = client.post("/auth/register", json=REGISTER_PAYLOAD)
    assert resp.status_code == 409


def test_login_success(client):
    client.post("/auth/register", json=REGISTER_PAYLOAD)
    resp = client.post("/auth/login", data={
        "username": REGISTER_PAYLOAD["email"],
        "password": REGISTER_PAYLOAD["password"],
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json=REGISTER_PAYLOAD)
    resp = client.post("/auth/login", data={
        "username": REGISTER_PAYLOAD["email"],
        "password": "wrongpassword",
    })
    assert resp.status_code in (400, 401, 422)


def test_me_authenticated(client, auth_headers):
    resp = client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert "email" in resp.json()


def test_me_unauthenticated(client):
    resp = client.get("/auth/me")
    assert resp.status_code in (401, 403)
