"""
Match routes -- full CRUD for item matches.
Supports filtering by status and match_type.

Author: Vikas Reddy Amanagantti (x25178849)
"""

from flask import Blueprint, request, jsonify
from models import db, Match

match_bp = Blueprint("matches", __name__)


@match_bp.route("/api/matches", methods=["GET"])
def get_matches():
    """Retrieve all matches with optional filters."""
    try:
        query = Match.query
        status = request.args.get("status")
        match_type = request.args.get("match_type")

        if status:
            query = query.filter_by(status=status)
        if match_type:
            query = query.filter_by(match_type=match_type)

        matches = query.order_by(Match.created_at.desc()).all()
        return jsonify([m.to_dict() for m in matches]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@match_bp.route("/api/matches/<int:match_id>", methods=["GET"])
def get_match(match_id):
    """Retrieve a single match by its ID."""
    try:
        match = Match.query.get(match_id)
        if match is None:
            return jsonify({"error": "Match not found"}), 404
        return jsonify(match.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@match_bp.route("/api/matches", methods=["POST"])
def create_match():
    """Create a new match between a lost and found item."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        required = ["lost_item_id", "found_item_id", "confidence_score"]
        for field in required:
            if field not in data:
                return jsonify({"error": f"'{field}' is required"}), 400

        match = Match(
            lost_item_id=data["lost_item_id"],
            found_item_id=data["found_item_id"],
            confidence_score=data["confidence_score"],
            match_type=data.get("match_type", "text"),
            status=data.get("status", "pending"),
            notes=data.get("notes"),
        )
        db.session.add(match)
        db.session.commit()
        return jsonify(match.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@match_bp.route("/api/matches/<int:match_id>", methods=["PUT"])
def update_match(match_id):
    """Update an existing match."""
    try:
        match = Match.query.get(match_id)
        if match is None:
            return jsonify({"error": "Match not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        updatable = ["confidence_score", "match_type", "status", "notes"]
        for field in updatable:
            if field in data:
                setattr(match, field, data[field])

        db.session.commit()
        return jsonify(match.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@match_bp.route("/api/matches/<int:match_id>", methods=["DELETE"])
def delete_match(match_id):
    """Delete a match by its ID."""
    try:
        match = Match.query.get(match_id)
        if match is None:
            return jsonify({"error": "Match not found"}), 404
        db.session.delete(match)
        db.session.commit()
        return jsonify({"message": "Match deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
