"""
campusfinder -- A custom OOP library for the Smart Campus Lost & Found System.

Provides text-based item matching, campus location tracking, claim processing
workflows, notification management, and analytics utilities.

Author: Vikas Reddy Amanagantti (x25178849)
"""

from .item_matcher import ItemMatcher
from .location_tracker import LocationTracker
from .claim_processor import ClaimProcessor
from .notification_manager import NotificationManager
from .analytics import Analytics

__version__ = "1.0.0"

__all__ = [
    "ItemMatcher",
    "LocationTracker",
    "ClaimProcessor",
    "NotificationManager",
    "Analytics",
]
