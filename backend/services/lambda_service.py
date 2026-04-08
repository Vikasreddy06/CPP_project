"""
AWS Lambda service wrapper.
Triggers asynchronous image processing and match detection functions.
Falls back to synchronous mock execution when USE_AWS is False.

Author: Vikas Reddy Amanagantti (x25178849)
"""

import json
import uuid
import random
from datetime import datetime, timezone


class LambdaService:
    """Encapsulates all interactions with AWS Lambda."""

    def __init__(self, app=None):
        self.app = app
        self.use_aws = False
        self.client = None
        # Mock invocation log
        self._invocations = []
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialise the service with Flask app configuration."""
        self.app = app
        self.use_aws = app.config.get("USE_AWS", False)
        self.region = app.config.get("AWS_REGION", "eu-west-1")
        self.function_name = app.config.get("LAMBDA_FUNCTION_NAME", "campus-image-processor")
        if self.use_aws:
            import boto3
            self.client = boto3.client("lambda", region_name=self.region)

    def invoke_image_processor(self, item_id, image_url):
        """
        Invoke the image processing Lambda function asynchronously.

        Args:
            item_id: ID of the item whose image should be processed.
            image_url: URL of the image in S3.

        Returns:
            A dict with 'invocation_id' and 'status'.
        """
        payload = {
            "item_id": str(item_id),
            "image_url": image_url,
            "action": "process_image",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if self.use_aws:
            response = self.client.invoke(
                FunctionName=self.function_name,
                InvocationType="Event",  # asynchronous
                Payload=json.dumps(payload),
            )
            return {
                "invocation_id": response.get("ResponseMetadata", {}).get("RequestId", ""),
                "status": "invoked",
                "status_code": response["StatusCode"],
            }
        else:
            invocation = {
                "invocation_id": str(uuid.uuid4()),
                "function": self.function_name,
                "payload": payload,
                "status": "mock_completed",
                "result": {
                    "labels_detected": ["Electronics", "Phone", "Black"],
                    "category_suggestion": "electronics",
                    "processing_time_ms": random.randint(120, 800),
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self._invocations.append(invocation)
            return {
                "invocation_id": invocation["invocation_id"],
                "status": "mock_completed",
                "result": invocation["result"],
            }

    def invoke_match_detector(self, lost_item_id, found_item_ids):
        """
        Invoke the match detection Lambda function to compare a lost item
        against a list of found items.

        Args:
            lost_item_id: ID of the lost item.
            found_item_ids: List of found item IDs to compare against.

        Returns:
            A dict with match results.
        """
        payload = {
            "lost_item_id": str(lost_item_id),
            "found_item_ids": [str(fid) for fid in found_item_ids],
            "action": "detect_matches",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if self.use_aws:
            response = self.client.invoke(
                FunctionName=f"{self.function_name}-matcher",
                InvocationType="RequestResponse",
                Payload=json.dumps(payload),
            )
            result = json.loads(response["Payload"].read())
            return result
        else:
            # Simulate match results
            matches = []
            for fid in found_item_ids:
                confidence = round(random.uniform(0.3, 0.95), 2)
                matches.append({
                    "found_item_id": str(fid),
                    "confidence": confidence,
                    "match_type": "combined",
                    "is_match": confidence > 0.6,
                })
            invocation = {
                "invocation_id": str(uuid.uuid4()),
                "function": f"{self.function_name}-matcher",
                "payload": payload,
                "status": "mock_completed",
                "result": {"matches": matches},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self._invocations.append(invocation)
            return {
                "invocation_id": invocation["invocation_id"],
                "status": "mock_completed",
                "matches": matches,
            }

    def get_invocation_log(self):
        """Return the log of all mock Lambda invocations."""
        return self._invocations

    def get_status(self):
        """Return a status dictionary describing the Lambda connection."""
        return {
            "service": "AWS Lambda",
            "status": "connected" if self.use_aws else "mock",
            "function_name": self.function_name,
            "invocations": len(self._invocations),
            "description": "Serverless functions for async image processing and match detection",
        }
