"""
Amazon S3 service wrapper.
Handles image uploads and retrieval for lost/found items.
Falls back to local filesystem storage when USE_AWS is False.

Author: Vikas Reddy Amanagantti (x25178849)
"""

import os
import uuid
import base64
from datetime import datetime, timezone


class S3Service:
    """Encapsulates all interactions with Amazon S3."""

    def __init__(self, app=None):
        self.app = app
        self.use_aws = False
        self.client = None
        self.bucket = "campus-lost-found-images"
        # Mock storage: key -> {"data": bytes, "content_type": str, "uploaded_at": str}
        self._mock_store = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialise the service with Flask app configuration."""
        self.app = app
        self.use_aws = app.config.get("USE_AWS", False)
        self.bucket = app.config.get("S3_BUCKET", "campus-lost-found-images")
        self.region = app.config.get("AWS_REGION", "eu-west-1")
        if self.use_aws:
            import boto3
            self.client = boto3.client("s3", region_name=self.region)

    def upload_image(self, file_data, filename=None, content_type="image/jpeg"):
        """
        Upload an image and return its URL.

        Args:
            file_data: Raw bytes of the image.
            filename: Optional filename; a UUID-based name is generated if omitted.
            content_type: MIME type of the image.

        Returns:
            A URL string pointing to the uploaded image.
        """
        if filename is None:
            ext = content_type.split("/")[-1] if "/" in content_type else "jpg"
            filename = f"items/{uuid.uuid4()}.{ext}"

        if self.use_aws:
            self.client.put_object(
                Bucket=self.bucket,
                Key=filename,
                Body=file_data,
                ContentType=content_type,
            )
            return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{filename}"
        else:
            # Store in memory and return a mock URL
            self._mock_store[filename] = {
                "data": file_data if isinstance(file_data, bytes) else b"mock-image-data",
                "content_type": content_type,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
            }
            return f"http://localhost:5001/mock-s3/{filename}"

    def get_image_url(self, key):
        """
        Generate a pre-signed URL (or mock URL) for the given S3 key.

        Args:
            key: The S3 object key.

        Returns:
            A URL string.
        """
        if self.use_aws:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=3600,
            )
            return url
        else:
            return f"http://localhost:5001/mock-s3/{key}"

    def delete_image(self, key):
        """
        Delete an image from S3 or the mock store.

        Args:
            key: The S3 object key.

        Returns:
            True if deletion succeeded.
        """
        if self.use_aws:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            return True
        else:
            self._mock_store.pop(key, None)
            return True

    def list_images(self, prefix="items/"):
        """
        List all images under the given prefix.

        Args:
            prefix: Key prefix to filter by.

        Returns:
            A list of object key strings.
        """
        if self.use_aws:
            response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
            return [obj["Key"] for obj in response.get("Contents", [])]
        else:
            return [k for k in self._mock_store if k.startswith(prefix)]

    def get_status(self):
        """Return a status dictionary describing the S3 connection."""
        return {
            "service": "Amazon S3",
            "status": "connected" if self.use_aws else "mock",
            "bucket": self.bucket,
            "stored_objects": len(self._mock_store) if not self.use_aws else "N/A",
            "description": "Object storage for item images and evidence photos",
        }
