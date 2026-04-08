"""
Item model for the Smart Campus Lost & Found System.
Represents both lost and found items reported on campus.

Author: Vikas Reddy Amanagantti (x25178849)
"""

from datetime import datetime, timezone
from .database import db


class Item(db.Model):
    """SQLAlchemy model for a lost or found item."""

    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)          # electronics, clothing, accessories, books, keys, other
    color = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(200), nullable=False)          # campus building / zone
    image_url = db.Column(db.String(500), nullable=True)
    item_type = db.Column(db.String(10), nullable=False)          # lost | found
    status = db.Column(db.String(20), nullable=False, default="open")  # open | matched | claimed | closed
    contact_info = db.Column(db.String(200), nullable=True)
    date_reported = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    date_resolved = db.Column(db.DateTime, nullable=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Relationships for matches
    lost_matches = db.relationship("Match", foreign_keys="Match.lost_item_id", backref="lost_item", lazy=True)
    found_matches = db.relationship("Match", foreign_keys="Match.found_item_id", backref="found_item", lazy=True)
    claims = db.relationship("Claim", backref="item", lazy=True)

    def to_dict(self):
        """Serialise the item to a JSON-friendly dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "color": self.color,
            "location": self.location,
            "image_url": self.image_url,
            "item_type": self.item_type,
            "status": self.status,
            "contact_info": self.contact_info,
            "date_reported": self.date_reported.isoformat() if self.date_reported else None,
            "date_resolved": self.date_resolved.isoformat() if self.date_resolved else None,
            "reporter_id": self.reporter_id,
        }

    def __repr__(self):
        return f"<Item {self.item_type}: {self.title}>"
