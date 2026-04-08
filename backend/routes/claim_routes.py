"""
Claim routes -- full CRUD for item claims.
Supports filtering by status and item_id.

Author: Vikas Reddy Amanagantti (x25178849)
"""

from flask import Blueprint, request, jsonify
from models import db, Claim
from datetime import datetime, timezone

claim_bp = Blueprint("claims", __name__)


@claim_bp.route("/api/claims", methods=["GET"])
def get_claims():
    """Retrieve all claims with optional filters."""
    try:
        query = Claim.query
        status = request.args.get("status")
        item_id = request.args.get("item_id")

        if status:
            query = query.filter_by(status=status)
        if item_id:
            query = query.filter_by(item_id=int(item_id))

        claims = query.order_by(Claim.date_claimed.desc()).all()
        return jsonify([c.to_dict() for c in claims]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@claim_bp.route("/api/claims/<int:claim_id>", methods=["GET"])
def get_claim(claim_id):
    """Retrieve a single claim by its ID."""
    try:
        claim = Claim.query.get(claim_id)
        if claim is None:
            return jsonify({"error": "Claim not found"}), 404
        return jsonify(claim.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@claim_bp.route("/api/claims", methods=["POST"])
def create_claim():
    """Create a new claim on an item."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        required = ["item_id", "claimant_id", "description"]
        for field in required:
            if field not in data:
                return jsonify({"error": f"'{field}' is required"}), 400

        claim = Claim(
            item_id=data["item_id"],
            claimant_id=data["claimant_id"],
            description=data["description"],
            evidence=data.get("evidence"),
            status=data.get("status", "pending"),
            priority=data.get("priority", 0),
        )
        db.session.add(claim)
        db.session.commit()
        return jsonify(claim.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@claim_bp.route("/api/claims/<int:claim_id>", methods=["PUT"])
def update_claim(claim_id):
    """Update an existing claim."""
    try:
        claim = Claim.query.get(claim_id)
        if claim is None:
            return jsonify({"error": "Claim not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        updatable = ["description", "evidence", "status", "priority"]
        for field in updatable:
            if field in data:
                setattr(claim, field, data[field])

        if data.get("status") in ("approved", "rejected") and claim.date_resolved is None:
            claim.date_resolved = datetime.now(timezone.utc)

        db.session.commit()
        return jsonify(claim.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@claim_bp.route("/api/claims/<int:claim_id>", methods=["DELETE"])
def delete_claim(claim_id):
    """Delete a claim by its ID."""
    try:
        claim = Claim.query.get(claim_id)
        if claim is None:
            return jsonify({"error": "Claim not found"}), 404
        db.session.delete(claim)
        db.session.commit()
        return jsonify({"message": "Claim deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
