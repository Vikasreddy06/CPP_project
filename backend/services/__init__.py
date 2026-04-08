"""
AWS service wrappers for the Smart Campus Lost & Found System.
Each service class supports a mock mode for local development.
"""

from .dynamodb_service import DynamoDBService
from .s3_service import S3Service
from .rekognition_service import RekognitionService
from .sns_service import SNSService
from .cloudwatch_service import CloudWatchService
from .lambda_service import LambdaService

__all__ = [
    "DynamoDBService",
    "S3Service",
    "RekognitionService",
    "SNSService",
    "CloudWatchService",
    "LambdaService",
]
