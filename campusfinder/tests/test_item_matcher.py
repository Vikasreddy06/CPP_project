"""
Tests for the ItemMatcher class.

Author: Vikas Reddy Amanagantti (x25178849)
"""

import pytest
from campusfinder import ItemMatcher


@pytest.fixture
def matcher():
    return ItemMatcher()


# -- Cosine similarity --

def test_cosine_identical_texts(matcher):
    score = matcher.cosine_similarity("black iphone 15 pro", "black iphone 15 pro")
    assert score == pytest.approx(1.0, abs=0.01)


def test_cosine_completely_different(matcher):
    score = matcher.cosine_similarity("red umbrella large", "blue laptop small")
    assert score < 0.3


def test_cosine_partial_overlap(matcher):
    score = matcher.cosine_similarity("silver macbook laptop", "silver laptop charger")
    assert 0.2 < score < 0.9


def test_cosine_empty_string(matcher):
    assert matcher.cosine_similarity("", "some text") == 0.0


# -- Jaccard similarity --

def test_jaccard_identical(matcher):
    score = matcher.jaccard_similarity("lost black phone", "lost black phone")
    assert score == pytest.approx(1.0, abs=0.01)


def test_jaccard_no_overlap(matcher):
    score = matcher.jaccard_similarity("red umbrella", "blue laptop")
    assert score == 0.0


def test_jaccard_partial(matcher):
    score = matcher.jaccard_similarity("black phone case", "black phone charger")
    assert 0.3 < score < 0.9


def test_jaccard_empty(matcher):
    assert matcher.jaccard_similarity("", "") == 0.0


# -- Fuzzy matching --

def test_fuzzy_identical(matcher):
    score = matcher.fuzzy_match_score("iphone", "iphone")
    assert score == pytest.approx(1.0, abs=0.01)


def test_fuzzy_similar(matcher):
    score = matcher.fuzzy_match_score("iphone 15", "iphone 14")
    assert score > 0.5


def test_fuzzy_different(matcher):
    score = matcher.fuzzy_match_score("umbrella", "keyboard")
    assert score < 0.5


# -- Category matching --

def test_category_exact_match(matcher):
    assert matcher.category_match_score("electronics", "electronics") == 1.0


def test_category_related(matcher):
    assert matcher.category_match_score("electronics", "gadgets") == 0.5


def test_category_unrelated(matcher):
    assert matcher.category_match_score("electronics", "clothing") == 0.0


def test_category_none(matcher):
    assert matcher.category_match_score(None, "electronics") == 0.0


# -- Color matching --

def test_color_exact(matcher):
    assert matcher.color_match_score("black", "black") == 1.0


def test_color_similar(matcher):
    assert matcher.color_match_score("black", "charcoal") == 0.5


def test_color_different(matcher):
    assert matcher.color_match_score("red", "blue") == 0.0


def test_color_none(matcher):
    assert matcher.color_match_score(None, "blue") == 0.0


# -- Composite matching --

def test_composite_high_match(matcher):
    lost = {"description": "black iPhone 15 pro max", "category": "electronics", "color": "black"}
    found = {"description": "black iPhone 15 phone", "category": "electronics", "color": "black"}
    result = matcher.compute_match_score(lost, found)
    assert result["overall"] > 0.5
    assert result["is_likely_match"] is True


def test_composite_low_match(matcher):
    lost = {"description": "red umbrella large", "category": "accessories", "color": "red"}
    found = {"description": "blue laptop dell", "category": "electronics", "color": "blue"}
    result = matcher.compute_match_score(lost, found)
    assert result["overall"] < 0.3
    assert result["is_likely_match"] is False


# -- Best matches --

def test_find_best_matches(matcher):
    lost = {"description": "silver laptop macbook", "category": "electronics", "color": "silver"}
    found_items = [
        {"description": "silver macbook pro laptop", "category": "electronics", "color": "silver"},
        {"description": "red umbrella", "category": "accessories", "color": "red"},
        {"description": "silver laptop charger", "category": "electronics", "color": "silver"},
    ]
    results = matcher.find_best_matches(lost, found_items, top_n=2)
    assert len(results) == 2
    # The macbook should rank first
    assert results[0][1]["overall"] >= results[1][1]["overall"]
