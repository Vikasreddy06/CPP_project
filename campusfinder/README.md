# campusfinder-vikasreddy

A custom OOP library for the Smart Campus Lost & Found System, providing text-based item matching, campus location tracking, claim processing workflows, notification management, and analytics utilities.

The package is published on PyPI as `campusfinder-vikasreddy` and imported as `campusfinder`.

## Installation

```bash
pip install campusfinder-vikasreddy
```

Or for local development:

```bash
pip install -e .
```

## Classes

- **ItemMatcher** -- cosine similarity, Jaccard similarity, fuzzy matching, category and colour matching
- **LocationTracker** -- campus zone management, Haversine distance, proximity search
- **ClaimProcessor** -- claim lifecycle, priority scoring, status transitions, audit logging
- **NotificationManager** -- rules engine, channel preferences, urgency filtering, batching
- **Analytics** -- recovery rates, category breakdowns, hotspot analysis, trend detection

## Usage

```python
from campusfinder import ItemMatcher

matcher = ItemMatcher()
score = matcher.compute_match_score(
    {"description": "black iPhone 15", "category": "electronics", "color": "black"},
    {"description": "black smartphone", "category": "electronics", "color": "black"},
)
print(score["overall"])  # e.g. 0.78
```

## Running Tests

```bash
pytest tests/ -v
```

## Author

Vikas Reddy Amanagantti (x25178849) -- National College of Ireland
