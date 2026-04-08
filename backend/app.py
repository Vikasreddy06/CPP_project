"""
Flask application factory for the Smart Campus Lost & Found System.
Creates and configures the Flask app, registers all blueprints, and
initialises AWS service wrappers.

Author: Vikas Reddy Amanagantti (x25178849)
"""

import os
import sys

# Ensure the backend package root is on the import path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS

from config import config_by_name
from models.database import db, init_db
from routes import item_bp, claim_bp, user_bp, match_bp, aws_bp
from services import (
    DynamoDBService,
    S3Service,
    RekognitionService,
    SNSService,
    CloudWatchService,
    LambdaService,
)


def create_app(config_name=None):
    """
    Application factory.

    Args:
        config_name: One of 'development', 'testing', or 'production'.
                     Defaults to the FLASK_ENV environment variable or
                     'development'.

    Returns:
        A fully configured Flask application instance.
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Enable CORS for the React frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialise the database
    init_db(app)

    # Initialise AWS service wrappers
    dynamodb_service = DynamoDBService(app)
    s3_service = S3Service(app)
    rekognition_service = RekognitionService(app)
    sns_service = SNSService(app)
    cloudwatch_service = CloudWatchService(app)
    lambda_service = LambdaService(app)

    # Store services on app.config so routes can access them
    app.config["AWS_SERVICES"] = {
        "dynamodb": dynamodb_service,
        "s3": s3_service,
        "rekognition": rekognition_service,
        "sns": sns_service,
        "cloudwatch": cloudwatch_service,
        "lambda": lambda_service,
    }

    # Register route blueprints
    app.register_blueprint(item_bp)
    app.register_blueprint(claim_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(match_bp)
    app.register_blueprint(aws_bp)

    # Root health-check endpoint
    @app.route("/")
    def index():
        return jsonify({
            "application": "Smart Campus Lost & Found System",
            "author": "Vikas Reddy Amanagantti (x25178849)",
            "version": "1.0.0",
            "status": "running",
            "aws_mode": "live" if app.config.get("USE_AWS") else "mock",
        })

    @app.route("/api/health")
    def health():
        return jsonify({"status": "healthy"}), 200

    return app


# Development server entry point
if __name__ == "__main__":
    application = create_app("development")
    application.run(host="0.0.0.0", port=5001, debug=True)
