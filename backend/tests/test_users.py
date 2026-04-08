"""
Tests for user routes -- covers full CRUD.

Author: Vikas Reddy Amanagantti (x25178849)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import create_app
from models import db


@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def _create_user(client, **overrides):
    payload = {
        "name": "Vikas Reddy",
        "email": "vikas@student.ncirl.ie",
        "student_id": "x25178849",
        "phone": "+353851234567",
        "role": "student",
    }
    payload.update(overrides)
    return client.post("/api/users", json=payload)


def test_create_user(client):
    resp = _create_user(client)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Vikas Reddy"
    assert data["role"] == "student"


def test_create_user_missing_fields(client):
    resp = client.post("/api/users", json={"name": "Incomplete"})
    assert resp.status_code == 400


def test_create_duplicate_email(client):
    _create_user(client)
    resp = _create_user(client, student_id="x00000002")
    assert resp.status_code == 409


def test_create_duplicate_student_id(client):
    _create_user(client)
    resp = _create_user(client, email="other@ncirl.ie")
    assert resp.status_code == 409


def test_get_all_users(client):
    _create_user(client)
    _create_user(client, name="Admin", email="admin@ncirl.ie",
                 student_id="x00000099", role="admin")
    resp = client.get("/api/users")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_get_user_by_id(client):
    create_resp = _create_user(client)
    uid = create_resp.get_json()["id"]
    resp = client.get(f"/api/users/{uid}")
    assert resp.status_code == 200
    assert resp.get_json()["id"] == uid


def test_get_user_not_found(client):
    resp = client.get("/api/users/9999")
    assert resp.status_code == 404


def test_filter_users_by_role(client):
    _create_user(client)
    _create_user(client, name="Staff", email="staff@ncirl.ie",
                 student_id="x00000010", role="staff")
    resp = client.get("/api/users?role=student")
    users = resp.get_json()
    assert all(u["role"] == "student" for u in users)


def test_update_user(client):
    create_resp = _create_user(client)
    uid = create_resp.get_json()["id"]
    resp = client.put(f"/api/users/{uid}", json={"name": "Vikas R. Amanagantti"})
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Vikas R. Amanagantti"


def test_update_user_not_found(client):
    resp = client.put("/api/users/9999", json={"name": "Ghost"})
    assert resp.status_code == 404


def test_delete_user(client):
    create_resp = _create_user(client)
    uid = create_resp.get_json()["id"]
    resp = client.delete(f"/api/users/{uid}")
    assert resp.status_code == 200
    assert client.get(f"/api/users/{uid}").status_code == 404


def test_delete_user_not_found(client):
    resp = client.delete("/api/users/9999")
    assert resp.status_code == 404
