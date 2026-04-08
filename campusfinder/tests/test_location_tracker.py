"""
Tests for the LocationTracker class.

Author: Vikas Reddy Amanagantti (x25178849)
"""

import pytest
from campusfinder import LocationTracker


@pytest.fixture
def tracker():
    return LocationTracker()


def test_list_zones(tracker):
    zones = tracker.list_zones()
    assert len(zones) >= 5
    names = [z["name"] for z in zones]
    assert "Library Complex" in names


def test_get_zone(tracker):
    zone = tracker.get_zone("library")
    assert zone is not None
    assert zone["name"] == "Library Complex"


def test_get_zone_not_found(tracker):
    assert tracker.get_zone("nonexistent") is None


def test_add_zone(tracker):
    tracker.add_zone("new_zone", "New Zone", 53.35, -6.26)
    assert tracker.get_zone("new_zone") is not None


def test_get_zone_for_building(tracker):
    zone = tracker.get_zone_for_building("Library Building A")
    assert zone == "library"


def test_get_zone_for_unknown_building(tracker):
    assert tracker.get_zone_for_building("Nonexistent Hall") is None


def test_get_buildings_in_zone(tracker):
    buildings = tracker.get_buildings_in_zone("library")
    assert "Library Building A" in buildings
    assert "Library Building B" in buildings


def test_haversine_zero_distance(tracker):
    dist = tracker.haversine_distance(53.35, -6.26, 53.35, -6.26)
    assert dist == pytest.approx(0.0, abs=0.01)


def test_haversine_positive_distance(tracker):
    dist = tracker.haversine_distance(53.35, -6.26, 53.36, -6.26)
    assert dist > 0


def test_distance_between_zones(tracker):
    dist = tracker.distance_between_zones("library", "sports_centre")
    assert dist is not None
    assert dist > 0


def test_distance_unknown_zone(tracker):
    assert tracker.distance_between_zones("library", "nowhere") is None


def test_are_nearby_true(tracker):
    assert tracker.are_nearby("Library Building A", "Library Building B", threshold_m=500)


def test_are_nearby_false(tracker):
    # With a very small threshold, distant buildings should not be nearby
    assert tracker.are_nearby("Library Building A", "Gym", threshold_m=1) is False


def test_find_items_in_zone(tracker):
    items = [
        {"title": "Phone", "location": "Library Building A"},
        {"title": "Keys", "location": "Gym"},
        {"title": "Book", "location": "Library Building B"},
    ]
    result = tracker.find_items_in_zone(items, "library")
    assert len(result) == 2


def test_find_nearby_items(tracker):
    items = [
        {"title": "Phone", "location": "Library Building A"},
        {"title": "Keys", "location": "Gym"},
    ]
    result = tracker.find_nearby_items(items, "Science Lab 1", threshold_m=500)
    assert len(result) >= 1
