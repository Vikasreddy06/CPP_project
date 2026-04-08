"""
ItemMatcher -- text similarity, fuzzy matching, and multi-signal item matching.

Compares lost and found item descriptions using cosine similarity on TF vectors,
Jaccard similarity on token sets, category matching, and colour matching to
produce an overall confidence score.

Author: Vikas Reddy Amanagantti (x25178849)
"""

import math
import re
from collections import Counter


class ItemMatcher:
    """
    Computes similarity scores between lost and found item descriptions
    using multiple text-based and attribute-based signals.
    """

    # Default weights for the composite score
    DEFAULT_WEIGHTS = {
        "text": 0.40,
        "category": 0.25,
        "color": 0.15,
        "fuzzy": 0.20,
    }

    # Common stop-words to exclude from similarity calculations
    STOP_WORDS = frozenset([
        "a", "an", "the", "is", "it", "in", "on", "at", "to", "for",
        "of", "and", "or", "was", "my", "i", "with", "has", "had",
        "this", "that", "its", "be", "been", "being", "have",
    ])

    def __init__(self, weights=None):
        """
        Initialise the matcher with optional custom signal weights.

        Args:
            weights: dict mapping signal names to floats that sum to 1.0.
        """
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()

    # ------------------------------------------------------------------
    # Tokenisation helpers
    # ------------------------------------------------------------------

    def _tokenise(self, text):
        """Lowercase, strip punctuation, remove stop-words, return token list."""
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        return [t for t in tokens if t not in self.STOP_WORDS]

    def _term_frequency(self, tokens):
        """Return a Counter representing term frequencies."""
        return Counter(tokens)

    # ------------------------------------------------------------------
    # Similarity algorithms
    # ------------------------------------------------------------------

    def cosine_similarity(self, text_a, text_b):
        """
        Compute cosine similarity between two text strings based on
        term-frequency vectors.

        Args:
            text_a: First text string.
            text_b: Second text string.

        Returns:
            A float between 0.0 and 1.0.
        """
        tf_a = self._term_frequency(self._tokenise(text_a))
        tf_b = self._term_frequency(self._tokenise(text_b))

        if not tf_a or not tf_b:
            return 0.0

        # Union of all terms
        all_terms = set(tf_a.keys()) | set(tf_b.keys())

        dot_product = sum(tf_a.get(t, 0) * tf_b.get(t, 0) for t in all_terms)
        mag_a = math.sqrt(sum(v ** 2 for v in tf_a.values()))
        mag_b = math.sqrt(sum(v ** 2 for v in tf_b.values()))

        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot_product / (mag_a * mag_b)

    def jaccard_similarity(self, text_a, text_b):
        """
        Compute Jaccard similarity (intersection / union) on token sets.

        Args:
            text_a: First text string.
            text_b: Second text string.

        Returns:
            A float between 0.0 and 1.0.
        """
        set_a = set(self._tokenise(text_a))
        set_b = set(self._tokenise(text_b))

        if not set_a and not set_b:
            return 0.0

        intersection = set_a & set_b
        union = set_a | set_b
        return len(intersection) / len(union)

    def fuzzy_match_score(self, text_a, text_b):
        """
        Compute a fuzzy similarity score using a simple character-level
        bigram overlap approach (Dice coefficient).

        Args:
            text_a: First text string.
            text_b: Second text string.

        Returns:
            A float between 0.0 and 1.0.
        """
        def bigrams(s):
            s = s.lower().strip()
            return [s[i:i + 2] for i in range(len(s) - 1)]

        bg_a = bigrams(text_a)
        bg_b = bigrams(text_b)

        if not bg_a or not bg_b:
            return 0.0

        set_a = set(bg_a)
        set_b = set(bg_b)
        overlap = set_a & set_b
        return 2 * len(overlap) / (len(set_a) + len(set_b))

    def category_match_score(self, category_a, category_b):
        """
        Return 1.0 if categories match exactly, 0.5 if they share a
        parent category, else 0.0.

        Args:
            category_a: Category string for the first item.
            category_b: Category string for the second item.

        Returns:
            A float: 0.0, 0.5, or 1.0.
        """
        if not category_a or not category_b:
            return 0.0
        if category_a.lower() == category_b.lower():
            return 1.0

        # Group related categories
        related_groups = [
            {"electronics", "gadgets", "devices"},
            {"clothing", "apparel", "garments"},
            {"accessories", "jewellery", "bags"},
            {"books", "notebooks", "documents"},
        ]
        a_lower, b_lower = category_a.lower(), category_b.lower()
        for group in related_groups:
            if a_lower in group and b_lower in group:
                return 0.5
        return 0.0

    def color_match_score(self, color_a, color_b):
        """
        Return 1.0 for an exact colour match, 0.5 for similar colours,
        else 0.0.

        Args:
            color_a: Colour string for the first item.
            color_b: Colour string for the second item.

        Returns:
            A float: 0.0, 0.5, or 1.0.
        """
        if not color_a or not color_b:
            return 0.0
        if color_a.lower() == color_b.lower():
            return 1.0

        similar_colors = [
            {"black", "dark grey", "charcoal"},
            {"white", "cream", "ivory"},
            {"red", "crimson", "maroon"},
            {"blue", "navy", "cobalt"},
            {"green", "olive", "emerald"},
        ]
        a_lower, b_lower = color_a.lower(), color_b.lower()
        for group in similar_colors:
            if a_lower in group and b_lower in group:
                return 0.5
        return 0.0

    # ------------------------------------------------------------------
    # Composite matching
    # ------------------------------------------------------------------

    def compute_match_score(self, lost_item, found_item):
        """
        Compute a weighted composite match score between a lost item and a
        found item.

        Args:
            lost_item: dict with keys 'description', 'category', 'color'.
            found_item: dict with keys 'description', 'category', 'color'.

        Returns:
            A dict with individual signal scores and the final 'overall' score.
        """
        desc_a = lost_item.get("description", "")
        desc_b = found_item.get("description", "")

        text_score = (self.cosine_similarity(desc_a, desc_b) +
                      self.jaccard_similarity(desc_a, desc_b)) / 2
        fuzzy_score = self.fuzzy_match_score(desc_a, desc_b)
        cat_score = self.category_match_score(
            lost_item.get("category", ""), found_item.get("category", ""))
        col_score = self.color_match_score(
            lost_item.get("color", ""), found_item.get("color", ""))

        overall = (
            self.weights["text"] * text_score +
            self.weights["fuzzy"] * fuzzy_score +
            self.weights["category"] * cat_score +
            self.weights["color"] * col_score
        )

        return {
            "text_similarity": round(text_score, 4),
            "fuzzy_similarity": round(fuzzy_score, 4),
            "category_match": round(cat_score, 4),
            "color_match": round(col_score, 4),
            "overall": round(overall, 4),
            "is_likely_match": overall >= 0.55,
        }

    def find_best_matches(self, lost_item, found_items, top_n=5):
        """
        Rank a list of found items by their match score against a lost item.

        Args:
            lost_item: dict describing the lost item.
            found_items: list of dicts describing found items.
            top_n: Maximum number of results to return.

        Returns:
            A sorted list of (found_item, score_dict) tuples, best first.
        """
        scored = []
        for fi in found_items:
            score = self.compute_match_score(lost_item, fi)
            scored.append((fi, score))
        scored.sort(key=lambda x: x[1]["overall"], reverse=True)
        return scored[:top_n]
