"""
Match model for the Smart Campus Lost & Found System.
Represents a suggested match between a lost item and a found item.

Author: Vikas Reddy Amanagantti (x25178849)
"""

from datetime import datetime, timezone
from .database import db


class Match(db.Model):
    """SQLAlchemy model for a match between a lost and found item."""

    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lost_item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    found_item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False, default=0.0)  # 0.0 – 1.0
    match_type = db.Column(db.String(30), nullable=False, default="text")  # text | image | combined
    status = db.Column(db.String(20), nullable=False, default="pending")   # pending | confirmed | rejected
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Serialise the match to a JSON-friendly dictionary."""
        return {
            "id": self.id,
            "lost_item_id": self.lost_item_id,
            "found_item_id": self.found_item_id,
            "confidence_score": self.confidence_score,
            "match_type": self.match_type,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Match Lost={self.lost_item_id} Found={self.found_item_id} ({self.confidence_score:.0%})>"
