"""Session CRUD route tests."""

import pytest


SESSION_PAYLOAD = {
    "candidate_name": "Marie Dupont",
    "candidate_role": "Développeuse Frontend",
    "candidate_email": "marie@example.com",
    "lsf_enabled": True,
}


def _create_session(client, headers):
    resp = client.post("/sessions/", json=SESSION_PAYLOAD, headers=headers)
    assert resp.status_code in (200, 201), resp.text
    return resp.json()


def test_create_session(client, auth_headers):
    data = _create_session(client, auth_headers)
    assert data["candidate_name"] == SESSION_PAYLOAD["candidate_name"]
    assert "session_id" in data
    assert "join_url_candidate" in data


def test_list_sessions(client, auth_headers):
    _create_session(client, auth_headers)
    resp = client.get("/sessions/", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


def test_get_session(client, auth_headers):
    created = _create_session(client, auth_headers)
    sid = created["session_id"]
    resp = client.get(f"/sessions/{sid}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["session_id"] == sid


def test_get_nonexistent_session(client, auth_headers):
    resp = client.get("/sessions/does-not-exist", headers=auth_headers)
    assert resp.status_code == 404


def test_patch_session_notes(client, auth_headers):
    sid = _create_session(client, auth_headers)["session_id"]
    resp = client.patch(f"/sessions/{sid}", json={"notes": "Bon candidat"}, headers=auth_headers)
    assert resp.status_code == 200

    detail = client.get(f"/sessions/{sid}", headers=auth_headers).json()
    assert detail["notes"] == "Bon candidat"


def test_patch_session_decision(client, auth_headers):
    sid = _create_session(client, auth_headers)["session_id"]
    resp = client.patch(f"/sessions/{sid}", json={"decision": "retained"}, headers=auth_headers)
    assert resp.status_code == 200


def test_patch_session_rating(client, auth_headers):
    sid = _create_session(client, auth_headers)["session_id"]
    resp = client.patch(f"/sessions/{sid}", json={"rating": 4}, headers=auth_headers)
    assert resp.status_code == 200

    detail = client.get(f"/sessions/{sid}", headers=auth_headers).json()
    assert detail["rating"] == 4


def test_patch_rating_out_of_range(client, auth_headers):
    sid = _create_session(client, auth_headers)["session_id"]
    resp = client.patch(f"/sessions/{sid}", json={"rating": 6}, headers=auth_headers)
    assert resp.status_code == 422


def test_patch_invalid_decision(client, auth_headers):
    sid = _create_session(client, auth_headers)["session_id"]
    resp = client.patch(f"/sessions/{sid}", json={"decision": "maybe"}, headers=auth_headers)
    assert resp.status_code == 422
