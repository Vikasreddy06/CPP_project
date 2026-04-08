"""
Tests for claim routes -- covers full CRUD.

Author: Vikas Reddy Amanagantti (x25178849)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import create_app
from models import db, User, Item


@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Seed a user and an item for claim tests
            user = User(name="Test User", email="test@ncirl.ie", student_id="x00000001")
            db.session.add(user)
            db.session.flush()
            item = Item(
                title="Found Phone", description="Black iPhone",
                category="electronics", location="Library",
                item_type="found", reporter_id=user.id,
            )
            db.session.add(item)
            db.session.commit()
        yield client


def _get_seed_ids(client):
    """Retrieve the seeded user and item IDs."""
    users = client.get("/api/users").get_json()
    items = client.get("/api/items").get_json()
    return users[0]["id"], items[0]["id"]


def _create_claim(client, **overrides):
    user_id, item_id = _get_seed_ids(client)
    payload = {
        "item_id": item_id,
        "claimant_id": user_id,
        "description": "This is my phone, it has a blue case",
        "evidence": "I can provide the IMEI number",
    }
    payload.update(overrides)
    return client.post("/api/claims", json=payload)


def test_create_claim(client):
    resp = _create_claim(client)
    assert resp.status_code == 201
    assert resp.get_json()["status"] == "pending"


def test_create_claim_missing_fields(client):
    resp = client.post("/api/claims", json={"description": "incomplete"})
    assert resp.status_code == 400


def test_get_all_claims(client):
    _create_claim(client)
    resp = client.get("/api/claims")
    assert resp.status_code == 200
    assert len(resp.get_json()) >= 1


def test_get_claim_by_id(client):
    create_resp = _create_claim(client)
    cid = create_resp.get_json()["id"]
    resp = client.get(f"/api/claims/{cid}")
    assert resp.status_code == 200
    assert resp.get_json()["id"] == cid


def test_get_claim_not_found(client):
    resp = client.get("/api/claims/9999")
    assert resp.status_code == 404


def test_update_claim_status(client):
    create_resp = _create_claim(client)
    cid = create_resp.get_json()["id"]
    resp = client.put(f"/api/claims/{cid}", json={"status": "approved"})
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "approved"


def test_update_claim_not_found(client):
    resp = client.put("/api/claims/9999", json={"status": "rejected"})
    assert resp.status_code == 404


def test_delete_claim(client):
    create_resp = _create_claim(client)
    cid = create_resp.get_json()["id"]
    resp = client.delete(f"/api/claims/{cid}")
    assert resp.status_code == 200
    assert client.get(f"/api/claims/{cid}").status_code == 404


def test_delete_claim_not_found(client):
    resp = client.delete("/api/claims/9999")
    assert resp.status_code == 404


def test_filter_claims_by_status(client):
    _create_claim(client)
    resp = client.get("/api/claims?status=pending")
    claims = resp.get_json()
    assert all(c["status"] == "pending" for c in claims)
