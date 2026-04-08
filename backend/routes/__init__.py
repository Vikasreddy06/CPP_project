"""
Route blueprints for the Smart Campus Lost & Found System.
"""

from .item_routes import item_bp
from .claim_routes import claim_bp
from .user_routes import user_bp
from .match_routes import match_bp
from .aws_routes import aws_bp

__all__ = ["item_bp", "claim_bp", "user_bp", "match_bp", "aws_bp"]
