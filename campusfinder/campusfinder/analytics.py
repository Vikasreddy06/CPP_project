"""
Analytics -- trend detection, recovery rates, hotspot analysis, and
time-to-recovery statistics for the Smart Campus Lost & Found System.

Author: Vikas Reddy Amanagantti (x25178849)
"""

from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict


class Analytics:
    """
    Computes statistical summaries and insights from lost-and-found data
    to identify trends, hotspots, and performance metrics.
    """

    def __init__(self):
        """Initialise with empty item store."""
        self._items = []

    def load_items(self, items):
        """
        Load a list of item dicts for analysis.

        Args:
            items: list of dicts, each with at least 'item_type', 'status',
                   'category', 'location', 'date_reported', and optionally
                   'date_resolved'.
        """
        self._items = list(items)

    # ------------------------------------------------------------------
    # Recovery metrics
    # ------------------------------------------------------------------

    def recovery_rate(self):
        """
        Calculate the percentage of lost items that were eventually closed
        (recovered).

        Returns:
            A float percentage (0-100), or 0 if no lost items exist.
        """
        lost = [i for i in self._items if i.get("item_type") == "lost"]
        if not lost:
            return 0.0
        recovered = sum(1 for i in lost if i.get("status") == "closed")
        return round((recovered / len(lost)) * 100, 2)

    def average_time_to_recovery(self):
        """
        Compute the mean time (in hours) from reporting to resolution for
        recovered items.

        Returns:
            A float representing average hours, or None if no data.
        """
        durations = []
        for item in self._items:
            if item.get("status") == "closed" and item.get("date_reported") and item.get("date_resolved"):
                reported = self._parse_date(item["date_reported"])
                resolved = self._parse_date(item["date_resolved"])
                if reported and resolved:
                    durations.append((resolved - reported).total_seconds() / 3600)
        if not durations:
            return None
        return round(sum(durations) / len(durations), 2)

    def median_time_to_recovery(self):
        """
        Compute the median time (in hours) from reporting to resolution.

        Returns:
            A float representing median hours, or None if no data.
        """
        durations = []
        for item in self._items:
            if item.get("status") == "closed" and item.get("date_reported") and item.get("date_resolved"):
                reported = self._parse_date(item["date_reported"])
                resolved = self._parse_date(item["date_resolved"])
                if reported and resolved:
                    durations.append((resolved - reported).total_seconds() / 3600)
        if not durations:
            return None
        durations.sort()
        n = len(durations)
        if n % 2 == 1:
            return round(durations[n // 2], 2)
        return round((durations[n // 2 - 1] + durations[n // 2]) / 2, 2)

    # ------------------------------------------------------------------
    # Category analysis
    # ------------------------------------------------------------------

    def category_breakdown(self):
        """
        Return a dict of category -> count for all items.

        Returns:
            dict mapping category strings to integer counts.
        """
        return dict(Counter(i.get("category", "unknown") for i in self._items))

    def top_lost_categories(self, n=5):
        """
        Return the most commonly lost categories.

        Args:
            n: Number of top categories to return.

        Returns:
            A list of (category, count) tuples.
        """
        lost = [i for i in self._items if i.get("item_type") == "lost"]
        return Counter(i.get("category", "unknown") for i in lost).most_common(n)

    # ------------------------------------------------------------------
    # Hotspot analysis
    # ------------------------------------------------------------------

    def location_hotspots(self, n=5):
        """
        Identify the locations where items are most frequently reported.

        Args:
            n: Number of top locations.

        Returns:
            A list of (location, count) tuples.
        """
        return Counter(i.get("location", "unknown") for i in self._items).most_common(n)

    def lost_hotspots(self, n=5):
        """Return top locations for lost items only."""
        lost = [i for i in self._items if i.get("item_type") == "lost"]
        return Counter(i.get("location", "unknown") for i in lost).most_common(n)

    def found_hotspots(self, n=5):
        """Return top locations for found items only."""
        found = [i for i in self._items if i.get("item_type") == "found"]
        return Counter(i.get("location", "unknown") for i in found).most_common(n)

    # ------------------------------------------------------------------
    # Trend detection
    # ------------------------------------------------------------------

    def daily_report_trend(self, days=30):
        """
        Count the number of items reported per day over the last N days.

        Args:
            days: Number of days to look back.

        Returns:
            A list of dicts with 'date' and 'count' keys.
        """
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=days)
        day_counts = defaultdict(int)

        for item in self._items:
            dt = self._parse_date(item.get("date_reported"))
            if dt and dt >= cutoff:
                day_str = dt.strftime("%Y-%m-%d")
                day_counts[day_str] += 1

        result = []
        for d in range(days):
            day = (cutoff + timedelta(days=d + 1)).strftime("%Y-%m-%d")
            result.append({"date": day, "count": day_counts.get(day, 0)})
        return result

    def weekly_summary(self):
        """
        Return a summary of items reported in the current week grouped by
        item_type.

        Returns:
            dict with 'lost' and 'found' counts.
        """
        now = datetime.now(timezone.utc)
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

        lost_count = 0
        found_count = 0
        for item in self._items:
            dt = self._parse_date(item.get("date_reported"))
            if dt and dt >= week_start:
                if item.get("item_type") == "lost":
                    lost_count += 1
                elif item.get("item_type") == "found":
                    found_count += 1
        return {"lost": lost_count, "found": found_count}

    # ------------------------------------------------------------------
    # Full dashboard report
    # ------------------------------------------------------------------

    def generate_report(self):
        """
        Produce a comprehensive analytics report dict suitable for
        dashboard display.

        Returns:
            dict with all computed analytics.
        """
        total = len(self._items)
        lost = sum(1 for i in self._items if i.get("item_type") == "lost")
        found = sum(1 for i in self._items if i.get("item_type") == "found")
        return {
            "total_items": total,
            "total_lost": lost,
            "total_found": found,
            "recovery_rate": self.recovery_rate(),
            "avg_recovery_hours": self.average_time_to_recovery(),
            "median_recovery_hours": self.median_time_to_recovery(),
            "category_breakdown": self.category_breakdown(),
            "top_lost_categories": self.top_lost_categories(),
            "location_hotspots": self.location_hotspots(),
            "weekly_summary": self.weekly_summary(),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_date(date_val):
        """
        Parse a date value that may be a string or datetime object.

        Returns:
            A timezone-aware datetime, or None on failure.
        """
        if date_val is None:
            return None
        if isinstance(date_val, datetime):
            if date_val.tzinfo is None:
                return date_val.replace(tzinfo=timezone.utc)
            return date_val
        try:
            dt = datetime.fromisoformat(str(date_val).replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, TypeError):
            return None
