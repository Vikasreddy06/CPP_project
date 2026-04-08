"""
Configuration module for Smart Campus Lost & Found System.
Supports development (SQLite + mocks), testing, and production (AWS) modes.

Author: Vikas Reddy Amanagantti (x25178849)
"""

import os


class Config:
    """Base configuration shared across all environments."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "campus-lost-found-secret-key-dev")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AWS toggle -- set to True only when real AWS credentials are available
    USE_AWS = os.environ.get("USE_AWS", "False").lower() in ("true", "1", "yes")

    # AWS region and resource names
    AWS_REGION = os.environ.get("AWS_REGION", "eu-west-1")
    DYNAMODB_TABLE_PREFIX = os.environ.get("DYNAMODB_TABLE_PREFIX", "campuslf_")
    S3_BUCKET = os.environ.get("S3_BUCKET", "campus-lost-found-images")
    SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "arn:aws:sns:eu-west-1:000000000000:campus-notifications")
    LAMBDA_FUNCTION_NAME = os.environ.get("LAMBDA_FUNCTION_NAME", "campus-image-processor")

    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


class DevelopmentConfig(Config):
    """Local development configuration -- SQLite + mock AWS services."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///campus_lost_found.db"
    )
    USE_AWS = False


class TestingConfig(Config):
    """Testing configuration -- in-memory SQLite, mocks always on."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    USE_AWS = False


class ProductionConfig(Config):
    """Production configuration -- DynamoDB as primary store, real AWS."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///campus_lost_found_prod.db"
    )
    USE_AWS = os.environ.get("USE_AWS", "True").lower() in ("true", "1", "yes")


# Convenience mapping used by the application factory
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
