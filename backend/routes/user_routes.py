"""
User routes -- full CRUD for campus users.
Supports filtering by role.

Author: Vikas Reddy Amanagantti (x25178849)
"""

from flask import Blueprint, request, jsonify
from models import db, User

user_bp = Blueprint("users", __name__)


@user_bp.route("/api/users", methods=["GET"])
def get_users():
    """Retrieve all users with optional role filter."""
    try:
        query = User.query
        role = request.args.get("role")
        if role:
            query = query.filter_by(role=role)

        users = query.order_by(User.created_at.desc()).all()
        return jsonify([u.to_dict() for u in users]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Retrieve a single user by their ID."""
    try:
        user = User.query.get(user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route("/api/users", methods=["POST"])
def create_user():
    """Create a new campus user."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        required = ["name", "email", "student_id"]
        for field in required:
            if field not in data:
                return jsonify({"error": f"'{field}' is required"}), 400

        # Check for duplicate email or student_id
        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "Email already registered"}), 409
        if User.query.filter_by(student_id=data["student_id"]).first():
            return jsonify({"error": "Student ID already registered"}), 409

        user = User(
            name=data["name"],
            email=data["email"],
            student_id=data["student_id"],
            phone=data.get("phone"),
            role=data.get("role", "student"),
        )
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@user_bp.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """Update an existing user's details."""
    try:
        user = User.query.get(user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        updatable = ["name", "email", "phone", "role"]
        for field in updatable:
            if field in data:
                setattr(user, field, data[field])

        db.session.commit()
        return jsonify(user.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@user_bp.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Delete a user by their ID."""
    try:
        user = User.query.get(user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
