"""
Item routes -- full CRUD for lost and found items.
Supports filtering by item_type (lost/found), category, and status.

Author: Vikas Reddy Amanagantti (x25178849)
"""

from flask import Blueprint, request, jsonify
from models import db, Item
from datetime import datetime, timezone

item_bp = Blueprint("items", __name__)


@item_bp.route("/api/items", methods=["GET"])
def get_items():
    """Retrieve all items with optional filters for type, category, and status."""
    try:
        query = Item.query
        item_type = request.args.get("type")
        category = request.args.get("category")
        status = request.args.get("status")
        search = request.args.get("search")

        if item_type:
            query = query.filter_by(item_type=item_type)
        if category:
            query = query.filter_by(category=category)
        if status:
            query = query.filter_by(status=status)
        if search:
            query = query.filter(
                db.or_(
                    Item.title.ilike(f"%{search}%"),
                    Item.description.ilike(f"%{search}%"),
                )
            )

        items = query.order_by(Item.date_reported.desc()).all()
        return jsonify([item.to_dict() for item in items]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@item_bp.route("/api/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """Retrieve a single item by its ID."""
    try:
        item = Item.query.get(item_id)
        if item is None:
            return jsonify({"error": "Item not found"}), 404
        return jsonify(item.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@item_bp.route("/api/items", methods=["POST"])
def create_item():
    """Create a new lost or found item."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        required = ["title", "description", "category", "location", "item_type"]
        for field in required:
            if field not in data:
                return jsonify({"error": f"'{field}' is required"}), 400

        if data["item_type"] not in ("lost", "found"):
            return jsonify({"error": "item_type must be 'lost' or 'found'"}), 400

        item = Item(
            title=data["title"],
            description=data["description"],
            category=data["category"],
            color=data.get("color"),
            location=data["location"],
            image_url=data.get("image_url"),
            item_type=data["item_type"],
            status=data.get("status", "open"),
            contact_info=data.get("contact_info"),
            reporter_id=data.get("reporter_id"),
        )
        db.session.add(item)
        db.session.commit()
        return jsonify(item.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@item_bp.route("/api/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    """Update an existing item by its ID."""
    try:
        item = Item.query.get(item_id)
        if item is None:
            return jsonify({"error": "Item not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        updatable = [
            "title", "description", "category", "color", "location",
            "image_url", "status", "contact_info", "reporter_id",
        ]
        for field in updatable:
            if field in data:
                setattr(item, field, data[field])

        # If status changes to closed, record the resolution time
        if data.get("status") == "closed" and item.date_resolved is None:
            item.date_resolved = datetime.now(timezone.utc)

        db.session.commit()
        return jsonify(item.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@item_bp.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """Delete an item by its ID."""
    try:
        item = Item.query.get(item_id)
        if item is None:
            return jsonify({"error": "Item not found"}), 404
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Item deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@item_bp.route("/api/items/stats", methods=["GET"])
def item_stats():
    """Return aggregate statistics about items."""
    try:
        total_lost = Item.query.filter_by(item_type="lost").count()
        total_found = Item.query.filter_by(item_type="found").count()
        open_items = Item.query.filter_by(status="open").count()
        matched_items = Item.query.filter_by(status="matched").count()
        claimed_items = Item.query.filter_by(status="claimed").count()
        closed_items = Item.query.filter_by(status="closed").count()
        total = total_lost + total_found
        recovery_rate = (closed_items / total * 100) if total > 0 else 0

        return jsonify({
            "total_items": total,
            "total_lost": total_lost,
            "total_found": total_found,
            "open_items": open_items,
            "matched_items": matched_items,
            "claimed_items": claimed_items,
            "closed_items": closed_items,
            "recovery_rate": round(recovery_rate, 1),
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
