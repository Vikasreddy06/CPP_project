"""
Tests for the Analytics class.

Author: Vikas Reddy Amanagantti (x25178849)
"""

import pytest
from datetime import datetime, timezone, timedelta
from campusfinder import Analytics


def _make_items():
    """Create a sample dataset for testing."""
    now = datetime.now(timezone.utc)
    return [
        {"item_type": "lost", "status": "closed", "category": "electronics",
         "location": "Library Building A", "date_reported": (now - timedelta(days=5)).isoformat(),
         "date_resolved": (now - timedelta(days=3)).isoformat()},
        {"item_type": "lost", "status": "open", "category": "electronics",
         "location": "Library Building A", "date_reported": (now - timedelta(days=2)).isoformat(),
         "date_resolved": None},
        {"item_type": "lost", "status": "closed", "category": "keys",
         "location": "Gym", "date_reported": (now - timedelta(days=10)).isoformat(),
         "date_resolved": (now - timedelta(days=7)).isoformat()},
        {"item_type": "found", "status": "open", "category": "clothing",
         "location": "Cafeteria", "date_reported": (now - timedelta(days=1)).isoformat(),
         "date_resolved": None},
        {"item_type": "found", "status": "closed", "category": "electronics",
         "location": "Library Building A", "date_reported": (now - timedelta(days=8)).isoformat(),
         "date_resolved": (now - timedelta(days=6)).isoformat()},
        {"item_type": "lost", "status": "open", "category": "accessories",
         "location": "Student Union", "date_reported": (now - timedelta(days=3)).isoformat(),
         "date_resolved": None},
    ]


@pytest.fixture
def analytics():
    a = Analytics()
    a.load_items(_make_items())
    return a


def test_recovery_rate(analytics):
    rate = analytics.recovery_rate()
    # 2 closed out of 4 lost = 50%
    assert rate == pytest.approx(50.0, abs=1)


def test_recovery_rate_empty():
    a = Analytics()
    a.load_items([])
    assert a.recovery_rate() == 0.0


def test_average_time_to_recovery(analytics):
    avg = analytics.average_time_to_recovery()
    assert avg is not None
    assert avg > 0


def test_median_time_to_recovery(analytics):
    median = analytics.median_time_to_recovery()
    assert median is not None
    assert median > 0


def test_category_breakdown(analytics):
    breakdown = analytics.category_breakdown()
    assert "electronics" in breakdown
    assert breakdown["electronics"] == 3


def test_top_lost_categories(analytics):
    top = analytics.top_lost_categories(n=3)
    assert len(top) >= 1
    # electronics should be the most common lost category
    assert top[0][0] == "electronics"


def test_location_hotspots(analytics):
    hotspots = analytics.location_hotspots()
    assert len(hotspots) >= 1
    # Library Building A appears most
    assert hotspots[0][0] == "Library Building A"


def test_lost_hotspots(analytics):
    hotspots = analytics.lost_hotspots()
    assert len(hotspots) >= 1


def test_found_hotspots(analytics):
    hotspots = analytics.found_hotspots()
    assert len(hotspots) >= 1


def test_daily_report_trend(analytics):
    trend = analytics.daily_report_trend(days=15)
    assert len(trend) == 15
    total_reported = sum(d["count"] for d in trend)
    assert total_reported >= 1


def test_weekly_summary(analytics):
    summary = analytics.weekly_summary()
    assert "lost" in summary
    assert "found" in summary


def test_generate_report(analytics):
    report = analytics.generate_report()
    assert "total_items" in report
    assert report["total_items"] == 6
    assert "recovery_rate" in report
    assert "category_breakdown" in report


def test_parse_date_none():
    assert Analytics._parse_date(None) is None


def test_parse_date_string():
    dt = Analytics._parse_date("2025-01-15T10:30:00")
    assert dt is not None
    assert dt.tzinfo is not None
