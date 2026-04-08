"""
AWS service status and utility routes.
Provides health-check endpoints for each cloud service and utility
endpoints for triggering image analysis and match detection.

Author: Vikas Reddy Amanagantti (x25178849)
"""

from flask import Blueprint, request, jsonify, current_app

aws_bp = Blueprint("aws", __name__)


@aws_bp.route("/api/aws/status", methods=["GET"])
def aws_status():
    """Return the connection status for every AWS service."""
    try:
        services = current_app.config.get("AWS_SERVICES", {})
        status = {}
        for name, svc in services.items():
            status[name] = svc.get_status()
        return jsonify({"aws_services": status}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@aws_bp.route("/api/aws/upload-image", methods=["POST"])
def upload_image():
    """Upload an item image to S3 (or mock store)."""
    try:
        s3 = current_app.config["AWS_SERVICES"]["s3"]
        if "file" in request.files:
            file = request.files["file"]
            image_url = s3.upload_image(
                file.read(),
                filename=f"items/{file.filename}",
                content_type=file.content_type or "image/jpeg",
            )
        else:
            # Accept base64 JSON body
            data = request.get_json()
            if not data or "image_data" not in data:
                return jsonify({"error": "No file or image_data provided"}), 400
            import base64
            image_bytes = base64.b64decode(data["image_data"])
            image_url = s3.upload_image(image_bytes)

        return jsonify({"image_url": image_url}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@aws_bp.route("/api/aws/analyse-image", methods=["POST"])
def analyse_image():
    """Run Rekognition label detection on an uploaded image."""
    try:
        rekognition = current_app.config["AWS_SERVICES"]["rekognition"]
        data = request.get_json()
        # Accept either raw bytes or a placeholder for mock mode
        image_bytes = b"mock-image-bytes"
        if data and "image_data" in data:
            import base64
            image_bytes = base64.b64decode(data["image_data"])

        result = rekognition.analyse_item_image(image_bytes)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@aws_bp.route("/api/aws/trigger-match", methods=["POST"])
def trigger_match():
    """Invoke the Lambda match detector for a lost item."""
    try:
        lambda_svc = current_app.config["AWS_SERVICES"]["lambda"]
        data = request.get_json()
        if not data or "lost_item_id" not in data:
            return jsonify({"error": "lost_item_id is required"}), 400

        found_ids = data.get("found_item_ids", [1, 2, 3])
        result = lambda_svc.invoke_match_detector(data["lost_item_id"], found_ids)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@aws_bp.route("/api/aws/notifications", methods=["GET"])
def get_notifications():
    """Return all sent notifications (mock mode only)."""
    try:
        sns = current_app.config["AWS_SERVICES"]["sns"]
        return jsonify({"notifications": sns.get_notifications()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@aws_bp.route("/api/aws/metrics", methods=["GET"])
def get_metrics():
    """Return CloudWatch metrics summary."""
    try:
        cw = current_app.config["AWS_SERVICES"]["cloudwatch"]
        return jsonify({"metrics": cw.get_metrics_summary()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@aws_bp.route("/api/aws/logs", methods=["GET"])
def get_logs():
    """Return recent CloudWatch log entries."""
    try:
        cw = current_app.config["AWS_SERVICES"]["cloudwatch"]
        limit = request.args.get("limit", 50, type=int)
        return jsonify({"logs": cw.get_recent_logs(limit)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
