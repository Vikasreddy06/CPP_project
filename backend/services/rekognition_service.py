"""
Amazon Rekognition service wrapper.
Provides image-based matching between lost and found items using
label detection and image comparison.
Falls back to simulated results when USE_AWS is False.

Author: Vikas Reddy Amanagantti (x25178849)
"""

import random
import hashlib
from datetime import datetime, timezone


# Mock label sets representing different item types
_MOCK_LABEL_SETS = [
    {
        "category": "clothing",
        "color": "Blue",
        "labels": [
            {"Name": "Clothing", "Confidence": 97.5},
            {"Name": "Shirt", "Confidence": 94.1},
            {"Name": "T-Shirt", "Confidence": 91.3},
            {"Name": "Blue", "Confidence": 88.7},
            {"Name": "Fabric", "Confidence": 82.4},
        ],
    },
    {
        "category": "electronics",
        "color": "Black",
        "labels": [
            {"Name": "Electronics", "Confidence": 95.2},
            {"Name": "Phone", "Confidence": 91.8},
            {"Name": "Mobile Phone", "Confidence": 89.3},
            {"Name": "Black", "Confidence": 85.1},
            {"Name": "Rectangle", "Confidence": 78.4},
        ],
    },
    {
        "category": "accessories",
        "color": "Brown",
        "labels": [
            {"Name": "Accessories", "Confidence": 96.0},
            {"Name": "Bag", "Confidence": 93.2},
            {"Name": "Handbag", "Confidence": 89.5},
            {"Name": "Brown", "Confidence": 86.3},
            {"Name": "Leather", "Confidence": 80.1},
        ],
    },
    {
        "category": "books",
        "color": "White",
        "labels": [
            {"Name": "Book", "Confidence": 96.8},
            {"Name": "Paper", "Confidence": 92.4},
            {"Name": "Text", "Confidence": 88.9},
            {"Name": "White", "Confidence": 84.2},
            {"Name": "Document", "Confidence": 79.6},
        ],
    },
    {
        "category": "keys",
        "color": "Silver",
        "labels": [
            {"Name": "Key", "Confidence": 95.7},
            {"Name": "Metal", "Confidence": 92.1},
            {"Name": "Silver", "Confidence": 87.8},
            {"Name": "Keychain", "Confidence": 83.5},
            {"Name": "Steel", "Confidence": 78.9},
        ],
    },
    {
        "category": "electronics",
        "color": "Silver",
        "labels": [
            {"Name": "Electronics", "Confidence": 96.3},
            {"Name": "Laptop", "Confidence": 94.5},
            {"Name": "Computer", "Confidence": 90.1},
            {"Name": "Silver", "Confidence": 86.7},
            {"Name": "Screen", "Confidence": 81.2},
        ],
    },
    {
        "category": "accessories",
        "color": "Black",
        "labels": [
            {"Name": "Sunglasses", "Confidence": 95.9},
            {"Name": "Eyewear", "Confidence": 92.6},
            {"Name": "Accessories", "Confidence": 89.0},
            {"Name": "Black", "Confidence": 85.4},
            {"Name": "Plastic", "Confidence": 79.3},
        ],
    },
    {
        "category": "clothing",
        "color": "Black",
        "labels": [
            {"Name": "Clothing", "Confidence": 96.8},
            {"Name": "Jacket", "Confidence": 93.7},
            {"Name": "Outerwear", "Confidence": 90.2},
            {"Name": "Black", "Confidence": 87.1},
            {"Name": "Fabric", "Confidence": 81.5},
        ],
    },
]


class RekognitionService:
    """Encapsulates all interactions with Amazon Rekognition."""

    def __init__(self, app=None):
        self.app = app
        self.use_aws = False
        self.client = None
        # Mock analysis history
        self._analysis_log = []
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialise the service with Flask app configuration."""
        self.app = app
        self.use_aws = app.config.get("USE_AWS", False)
        self.region = app.config.get("AWS_REGION", "eu-west-1")
        if self.use_aws:
            import boto3
            self.client = boto3.client("rekognition", region_name=self.region)

    def _pick_mock_labels(self, image_bytes):
        """Pick a consistent mock label set based on image content hash."""
        digest = hashlib.md5(image_bytes).hexdigest()
        index = int(digest, 16) % len(_MOCK_LABEL_SETS)
        return _MOCK_LABEL_SETS[index]

    def detect_labels(self, image_bytes):
        """
        Detect object labels in an image.

        Args:
            image_bytes: Raw bytes of the image.

        Returns:
            A list of dicts with 'Name' and 'Confidence' keys.
        """
        if self.use_aws:
            response = self.client.detect_labels(
                Image={"Bytes": image_bytes},
                MaxLabels=15,
                MinConfidence=70,
            )
            return response.get("Labels", [])
        else:
            label_set = self._pick_mock_labels(image_bytes)
            mock_labels = label_set["labels"]
            self._analysis_log.append({
                "type": "detect_labels",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "labels_found": len(mock_labels),
            })
            return mock_labels

    def compare_images(self, source_bytes, target_bytes):
        """
        Compare two images and return a similarity score.

        Args:
            source_bytes: Raw bytes of the first image (lost item).
            target_bytes: Raw bytes of the second image (found item).

        Returns:
            A dict with 'similarity' (0-100) and 'matched' (bool) keys.
        """
        if self.use_aws:
            response = self.client.compare_faces(
                SourceImage={"Bytes": source_bytes},
                TargetImage={"Bytes": target_bytes},
                SimilarityThreshold=70,
            )
            matches = response.get("FaceMatches", [])
            if matches:
                similarity = matches[0]["Similarity"]
            else:
                similarity = 0.0
            return {"similarity": similarity, "matched": similarity > 70}
        else:
            # Simulate a comparison result with controlled randomness
            similarity = round(random.uniform(55.0, 98.0), 2)
            result = {
                "similarity": similarity,
                "matched": similarity > 70,
                "source_labels": ["Electronics", "Phone"],
                "target_labels": ["Electronics", "Mobile Phone"],
                "common_labels": ["Electronics"],
            }
            self._analysis_log.append({
                "type": "compare_images",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "similarity": similarity,
            })
            return result

    def analyse_item_image(self, image_bytes):
        """
        Perform a full analysis of an item image: detect labels, estimate
        category and dominant colour.

        Args:
            image_bytes: Raw bytes of the image.

        Returns:
            A dict with 'labels', 'estimated_category', and 'dominant_color'.
        """
        labels = self.detect_labels(image_bytes)
        label_names = [l["Name"] for l in labels]

        # Simple heuristic category mapping
        category_map = {
            "Phone": "electronics",
            "Mobile Phone": "electronics",
            "Laptop": "electronics",
            "Computer": "electronics",
            "Book": "books",
            "Key": "keys",
            "Sunglasses": "accessories",
            "Eyewear": "accessories",
            "Bag": "accessories",
            "Handbag": "accessories",
            "Jacket": "clothing",
            "Shirt": "clothing",
            "T-Shirt": "clothing",
            "Clothing": "clothing",
            "Outerwear": "clothing",
        }
        category = "other"
        for label in label_names:
            if label in category_map:
                category = category_map[label]
                break

        # Detect dominant color from labels
        color_labels = [
            "Black", "White", "Red", "Blue", "Green", "Yellow",
            "Brown", "Silver", "Gold", "Orange", "Pink", "Grey", "Gray",
        ]
        dominant_color = "unknown"
        for label in label_names:
            if label in color_labels:
                dominant_color = label.lower()
                break

        # In mock mode, use the pre-set color from the label set
        if not self.use_aws:
            label_set = self._pick_mock_labels(image_bytes)
            dominant_color = label_set.get("color", dominant_color).lower()

        return {
            "labels": labels,
            "estimated_category": category,
            "dominant_color": dominant_color,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_status(self):
        """Return a status dictionary describing the Rekognition connection."""
        return {
            "service": "Amazon Rekognition",
            "status": "connected" if self.use_aws else "mock",
            "analyses_performed": len(self._analysis_log),
            "description": "Image recognition for matching lost and found items visually",
        }
