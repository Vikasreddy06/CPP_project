"""
Database models for the Smart Campus Lost & Found System.
Exports all SQLAlchemy models for convenient imports.
"""

from .database import db
from .user import User
from .item import Item
from .claim import Claim
from .match import Match

__all__ = ["db", "User", "Item", "Claim", "Match"]
