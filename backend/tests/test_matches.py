"""
Tests for match routes -- covers full CRUD with auto-calculated confidence.

Author: Vikas Reddy Amanagantti (x25178849)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import create_app
from models import db, Item


@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Seed a lost and a found item with matching descriptions
            lost = Item(title="Lost Phone", description="Black iPhone 15 Pro with clear case",
                        category="electronics", color="black", location="Library",
                        item_type="lost")
            found = Item(title="Found Phone", description="Black iPhone found near library with case",
                         category="electronics", color="black", location="Library entrance",
                         item_type="found")
            db.session.add_all([lost, found])
            db.session.commit()
        yield client


def _get_item_ids(client):
    items = client.get("/api/items").get_json()
    lost_id = next(i["id"] for i in items if i["item_type"] == "lost")
    found_id = next(i["id"] for i in items if i["item_type"] == "found")
    return lost_id, found_id


def _create_match(client, **overrides):
    lost_id, found_id = _get_item_ids(client)
    payload = {
        "lost_item_id": lost_id,
        "found_item_id": found_id,
        "match_type": "combined",
    }
    payload.update(overrides)
    return client.post("/api/matches", json=payload)


def test_create_match(client):
    resp = _create_match(client)
    assert resp.status_code == 201
    data = resp.get_json()
    # Confidence is auto-calculated, should be between 0 and 1
    assert 0 <= data["confidence_score"] <= 1
    assert data["status"] == "pending"


def test_create_match_missing_fields(client):
    resp = client.post("/api/matches", json={"notes": "incomplete"})
    assert resp.status_code == 400


def test_get_all_matches(client):
    _create_match(client)
    resp = client.get("/api/matches")
    assert resp.status_code == 200
    assert len(resp.get_json()) >= 1


def test_get_match_by_id(client):
    create_resp = _create_match(client)
    mid = create_resp.get_json()["id"]
    resp = client.get(f"/api/matches/{mid}")
    assert resp.status_code == 200
    assert resp.get_json()["id"] == mid


def test_get_match_not_found(client):
    resp = client.get("/api/matches/9999")
    assert resp.status_code == 404


def test_update_match(client):
    create_resp = _create_match(client)
    mid = create_resp.get_json()["id"]
    resp = client.put(f"/api/matches/{mid}", json={
        "status": "confirmed",
        "notes": "Verified by admin",
    })
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "confirmed"


def test_update_match_not_found(client):
    resp = client.put("/api/matches/9999", json={"status": "rejected"})
    assert resp.status_code == 404


def test_delete_match(client):
    create_resp = _create_match(client)
    mid = create_resp.get_json()["id"]
    resp = client.delete(f"/api/matches/{mid}")
    assert resp.status_code == 200
    assert client.get(f"/api/matches/{mid}").status_code == 404


def test_delete_match_not_found(client):
    resp = client.delete("/api/matches/9999")
    assert resp.status_code == 404


def test_filter_matches_by_status(client):
    _create_match(client)
    resp = client.get("/api/matches?status=pending")
    matches = resp.get_json()
    assert all(m["status"] == "pending" for m in matches)
