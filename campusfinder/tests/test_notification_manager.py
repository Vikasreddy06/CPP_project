"""
Tests for the NotificationManager class.

Author: Vikas Reddy Amanagantti (x25178849)
"""

import pytest
from campusfinder import NotificationManager


@pytest.fixture
def manager():
    nm = NotificationManager()
    nm.add_rule("match_found", "high",
                "A match was found for your item '{item_title}' with {confidence}% confidence.")
    nm.add_rule("claim_approved", "medium",
                "Your claim for '{item_title}' has been approved.")
    return nm


def test_set_and_get_preferences(manager):
    manager.set_user_preferences("u1", channels=["email", "push"], min_urgency="medium")
    prefs = manager.get_user_preferences("u1")
    assert "email" in prefs["channels"]
    assert "push" in prefs["channels"]
    assert prefs["min_urgency"] == "medium"


def test_default_preferences(manager):
    prefs = manager.get_user_preferences("unknown_user")
    assert "email" in prefs["channels"]


def test_create_notification(manager):
    notif = manager.create_notification("u1", "match_found", {
        "item_title": "Black Phone",
        "confidence": 85,
    })
    assert notif is not None
    assert "Black Phone" in notif["message"]
    assert notif["urgency"] == "high"


def test_notification_filtered_by_urgency(manager):
    manager.set_user_preferences("u2", min_urgency="critical")
    notif = manager.create_notification("u2", "match_found", {"item_title": "Phone", "confidence": 90})
    # high < critical, so notification should be filtered
    assert notif is None


def test_send_pending(manager):
    manager.create_notification("u1", "match_found", {"item_title": "Phone", "confidence": 90})
    manager.create_notification("u1", "claim_approved", {"item_title": "Phone"})
    count = manager.send_pending()
    assert count == 2
    assert manager.get_queue_size() == 0


def test_get_sent_notifications(manager):
    manager.create_notification("u1", "match_found", {"item_title": "X", "confidence": 80})
    manager.send_pending()
    sent = manager.get_sent_notifications("u1")
    assert len(sent) == 1


def test_batch_and_flush(manager):
    n1 = {"message": "Alert 1", "urgency": "medium"}
    n2 = {"message": "Alert 2", "urgency": "high"}
    manager.add_to_batch("u1", n1)
    manager.add_to_batch("u1", n2)
    summary = manager.flush_batch("u1")
    assert summary is not None
    assert summary["batched_count"] == 2
    assert "2 new notifications" in summary["message"]


def test_flush_empty_batch(manager):
    assert manager.flush_batch("u_empty") is None


def test_get_rules(manager):
    rules = manager.get_rules()
    assert len(rules) >= 2


def test_notification_stats(manager):
    manager.create_notification("u1", "match_found", {"item_title": "A", "confidence": 90})
    manager.send_pending()
    stats = manager.get_notification_stats()
    assert stats["total_sent"] >= 1


def test_unknown_event_type(manager):
    notif = manager.create_notification("u1", "some_unknown_event")
    assert notif is not None
    assert notif["urgency"] == "medium"
