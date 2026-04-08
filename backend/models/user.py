"""
User model for the Smart Campus Lost & Found System.
Represents students, staff, and administrators who interact with the platform.

Author: Vikas Reddy Amanagantti (x25178849)
"""

from datetime import datetime, timezone
from .database import db


class User(db.Model):
    """SQLAlchemy model for a campus user."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), nullable=False, default="student")  # student | staff | admin
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    items = db.relationship("Item", backref="reporter", lazy=True)
    claims = db.relationship("Claim", backref="claimant", lazy=True)

    def to_dict(self):
        """Serialise the user to a JSON-friendly dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "student_id": self.student_id,
            "phone": self.phone,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<User {self.name} ({self.student_id})>"
