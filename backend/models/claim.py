"""
Claim model for the Smart Campus Lost & Found System.
Represents a user's claim on a found item.

Author: Vikas Reddy Amanagantti (x25178849)
"""

from datetime import datetime, timezone
from .database import db


class Claim(db.Model):
    """SQLAlchemy model for an item claim."""

    __tablename__ = "claims"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    claimant_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    description = db.Column(db.Text, nullable=False)            # why the claimant believes this is theirs
    evidence = db.Column(db.Text, nullable=True)                 # additional proof or details
    status = db.Column(db.String(20), nullable=False, default="pending")  # pending | approved | rejected | withdrawn
    priority = db.Column(db.Integer, default=0)                  # computed by ClaimProcessor
    date_claimed = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    date_resolved = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        """Serialise the claim to a JSON-friendly dictionary."""
        return {
            "id": self.id,
            "item_id": self.item_id,
            "claimant_id": self.claimant_id,
            "description": self.description,
            "evidence": self.evidence,
            "status": self.status,
            "priority": self.priority,
            "date_claimed": self.date_claimed.isoformat() if self.date_claimed else None,
            "date_resolved": self.date_resolved.isoformat() if self.date_resolved else None,
        }

    def __repr__(self):
        return f"<Claim {self.id} for Item {self.item_id}>"
