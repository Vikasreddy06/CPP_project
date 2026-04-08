"""
Tests for item routes -- covers full CRUD and filtering.

Author: Vikas Reddy Amanagantti (x25178849)
"""

import json
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import create_app
from models import db


@pytest.fixture
def client():
    """Create a test client with an in-memory SQLite database."""
    app = create_app("testing")
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def _create_item(client, **overrides):
    """Helper to create an item via the API."""
    payload = {
        "title": "Lost Laptop",
        "description": "Silver MacBook Pro 14 inch",
        "category": "electronics",
        "color": "silver",
        "location": "Library Building A",
        "item_type": "lost",
        "contact_info": "vikas@student.ncirl.ie",
    }
    payload.update(overrides)
    return client.post("/api/items", json=payload)


# -------------------------------------------------------------------------
# CREATE tests
# -------------------------------------------------------------------------

def test_create_lost_item(client):
    """POST /api/items should create a lost item and return 201."""
    resp = _create_item(client)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["title"] == "Lost Laptop"
    assert data["item_type"] == "lost"
    assert data["status"] == "open"


def test_create_found_item(client):
    """POST /api/items should create a found item."""
    resp = _create_item(client, item_type="found", title="Found Umbrella")
    assert resp.status_code == 201
    assert resp.get_json()["item_type"] == "found"


def test_create_item_missing_fields(client):
    """POST /api/items with missing required fields should return 400."""
    resp = client.post("/api/items", json={"title": "Incomplete"})
    assert resp.status_code == 400


def test_create_item_invalid_type(client):
    """POST /api/items with invalid item_type should return 400."""
    resp = _create_item(client, item_type="stolen")
    assert resp.status_code == 400


# -------------------------------------------------------------------------
# READ tests
# -------------------------------------------------------------------------

def test_get_all_items_empty(client):
    """GET /api/items on an empty database should return an empty list."""
    resp = client.get("/api/items")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_get_all_items(client):
    """GET /api/items should return all created items."""
    _create_item(client)
    _create_item(client, title="Found Keys", item_type="found",
                 category="keys", location="Cafeteria")
    resp = client.get("/api/items")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_get_item_by_id(client):
    """GET /api/items/<id> should return a single item."""
    create_resp = _create_item(client)
    item_id = create_resp.get_json()["id"]
    resp = client.get(f"/api/items/{item_id}")
    assert resp.status_code == 200
    assert resp.get_json()["id"] == item_id


def test_get_item_not_found(client):
    """GET /api/items/9999 should return 404."""
    resp = client.get("/api/items/9999")
    assert resp.status_code == 404


def test_filter_items_by_type(client):
    """GET /api/items?type=lost should return only lost items."""
    _create_item(client, item_type="lost")
    _create_item(client, title="Found Wallet", item_type="found",
                 category="accessories", location="Gym")
    resp = client.get("/api/items?type=lost")
    items = resp.get_json()
    assert all(i["item_type"] == "lost" for i in items)


def test_filter_items_by_category(client):
    """GET /api/items?category=electronics should filter correctly."""
    _create_item(client, category="electronics")
    _create_item(client, title="Lost Scarf", category="clothing",
                 item_type="lost", location="Room 101")
    resp = client.get("/api/items?category=electronics")
    items = resp.get_json()
    assert all(i["category"] == "electronics" for i in items)


# -------------------------------------------------------------------------
# UPDATE tests
# -------------------------------------------------------------------------

def test_update_item(client):
    """PUT /api/items/<id> should update the item fields."""
    create_resp = _create_item(client)
    item_id = create_resp.get_json()["id"]
    resp = client.put(f"/api/items/{item_id}", json={"title": "Updated Laptop"})
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "Updated Laptop"


def test_update_item_not_found(client):
    """PUT /api/items/9999 should return 404."""
    resp = client.put("/api/items/9999", json={"title": "No Item"})
    assert resp.status_code == 404


# -------------------------------------------------------------------------
# DELETE tests
# -------------------------------------------------------------------------

def test_delete_item(client):
    """DELETE /api/items/<id> should remove the item."""
    create_resp = _create_item(client)
    item_id = create_resp.get_json()["id"]
    resp = client.delete(f"/api/items/{item_id}")
    assert resp.status_code == 200
    assert client.get(f"/api/items/{item_id}").status_code == 404


def test_delete_item_not_found(client):
    """DELETE /api/items/9999 should return 404."""
    resp = client.delete("/api/items/9999")
    assert resp.status_code == 404


# -------------------------------------------------------------------------
# Stats endpoint
# -------------------------------------------------------------------------

def test_item_stats(client):
    """GET /api/items/stats should return aggregate statistics."""
    _create_item(client, item_type="lost")
    _create_item(client, title="Found Keys", item_type="found",
                 category="keys", location="Cafeteria")
    resp = client.get("/api/items/stats")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total_lost"] == 1
    assert data["total_found"] == 1
    assert data["total_items"] == 2
