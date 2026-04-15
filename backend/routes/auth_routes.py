"""
Authentication routes -- register, login, and token verification.
Author: Vikas Reddy Amanagantti (x25178849)
"""

import hashlib
import hmac
import os
import json
import time
import base64
from flask import Blueprint, request, jsonify
from models import db, User

auth_bp = Blueprint("auth", __name__)

JWT_SECRET = os.environ.get("JWT_SECRET", "campuslf-secret-2026")


def _hash_password(password):
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return salt.hex() + ":" + key.hex()


def _verify_password(password, stored):
    parts = stored.split(":")
    if len(parts) != 2:
        return False
    salt = bytes.fromhex(parts[0])
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return hmac.compare_digest(key.hex(), parts[1])


def _create_token(user):
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode(json.dumps({
        "userId": user.id, "email": user.email, "name": user.name,
        "role": user.role, "exp": int(time.time()) + 86400,
    }).encode()).rstrip(b"=").decode()
    sig = hmac.new(JWT_SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
    s = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()
    return f"{header}.{payload}.{s}"


def _verify_token(token):
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        sig = hmac.new(JWT_SECRET.encode(), f"{parts[0]}.{parts[1]}".encode(), hashlib.sha256).digest()
        expected = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()
        if not hmac.compare_digest(expected, parts[2]):
            return None
        padding = 4 - len(parts[1]) % 4
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=" * padding))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        student_id = data.get("student_id", "").strip()
        role = data.get("role", "student")

        if not name or not email or not password or not student_id:
            return jsonify({"error": "Name, email, password, and student ID are required"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 409

        user = User(name=name, email=email, student_id=student_id,
                    role=role, password_hash=_hash_password(password))
        db.session.add(user)
        db.session.commit()

        token = _create_token(user)
        return jsonify({"message": "Registration successful", "token": token,
                        "user": user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = User.query.filter_by(email=email).first()
        if not user or not user.password_hash or not _verify_password(password, user.password_hash):
            return jsonify({"error": "Invalid email or password"}), 401

        token = _create_token(user)
        return jsonify({"message": "Login successful", "token": token,
                        "user": user.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/api/auth/me", methods=["GET"])
def get_me():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header[7:] if auth_header.startswith("Bearer ") else ""
    if not token:
        return jsonify({"error": "Token required"}), 401
    payload = _verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    return jsonify({"user": payload}), 200


@auth_bp.route("/api/auth/seed", methods=["POST"])
def seed_users():
    """Seed demo users for all three roles."""
    demo_users = [
        {"name": "Admin User", "email": "admin@campus.ie", "student_id": "ADMIN001", "role": "admin", "password": "Admin123!"},
        {"name": "Staff Member", "email": "staff@campus.ie", "student_id": "STAFF001", "role": "staff", "password": "Staff123!"},
        {"name": "Demo Student", "email": "student@campus.ie", "student_id": "STU25001", "role": "student", "password": "Student123!"},
    ]
    created = []
    for u in demo_users:
        if User.query.filter_by(email=u["email"]).first():
            continue
        user = User(name=u["name"], email=u["email"], student_id=u["student_id"],
                    role=u["role"], password_hash=_hash_password(u["password"]))
        db.session.add(user)
        created.append(u["email"])
    db.session.commit()
    return jsonify({"message": f"Seeded {len(created)} users", "created": created}), 200
