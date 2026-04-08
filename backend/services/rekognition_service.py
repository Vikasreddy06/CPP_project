"""
Amazon Rekognition service wrapper.
Provides image-based matching between lost and found items using
label detection and image comparison.
Falls back to simulated results when USE_AWS is False.

Author: Vikas Reddy Amanagantti (x25178849)
"""

import random
from datetime import datetime, timezone


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
            # Return realistic mock labels
            mock_labels = [
                {"Name": "Electronics", "Confidence": 95.2},
                {"Name": "Phone", "Confidence": 91.8},
                {"Name": "Mobile Phone", "Confidence": 89.3},
                {"Name": "Black", "Confidence": 85.1},
                {"Name": "Rectangle", "Confidence": 78.4},
            ]
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
            "Laptop": "electronics",
            "Book": "books",
            "Key": "keys",
            "Sunglasses": "accessories",
            "Bag": "accessories",
            "Jacket": "clothing",
            "Shirt": "clothing",
        }
        category = "other"
        for label in label_names:
            if label in category_map:
                category = category_map[label]
                break

        return {
            "labels": labels,
            "estimated_category": category,
            "dominant_color": "black",
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
