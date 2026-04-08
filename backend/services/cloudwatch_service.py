"""
Amazon CloudWatch service wrapper.
Provides application monitoring, custom metrics, and structured logging.
Falls back to in-memory metric/log storage when USE_AWS is False.

Author: Vikas Reddy Amanagantti (x25178849)
"""

from datetime import datetime, timezone
from collections import defaultdict


class CloudWatchService:
    """Encapsulates all interactions with Amazon CloudWatch."""

    def __init__(self, app=None):
        self.app = app
        self.use_aws = False
        self.client = None
        self.logs_client = None
        # Mock stores
        self._metrics = defaultdict(list)
        self._logs = []
        self._alarms = []
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialise the service with Flask app configuration."""
        self.app = app
        self.use_aws = app.config.get("USE_AWS", False)
        self.region = app.config.get("AWS_REGION", "eu-west-1")
        self.namespace = "CampusLostFound"
        if self.use_aws:
            import boto3
            self.client = boto3.client("cloudwatch", region_name=self.region)
            self.logs_client = boto3.client("logs", region_name=self.region)

    def put_metric(self, metric_name, value, unit="Count", dimensions=None):
        """
        Publish a custom metric data point.

        Args:
            metric_name: Name of the metric (e.g. 'ItemsReported').
            value: Numeric value.
            unit: CloudWatch unit (Count, Seconds, etc.).
            dimensions: Optional list of dicts with 'Name' and 'Value' keys.
        """
        timestamp = datetime.now(timezone.utc)

        if self.use_aws:
            metric_data = {
                "MetricName": metric_name,
                "Value": value,
                "Unit": unit,
                "Timestamp": timestamp,
            }
            if dimensions:
                metric_data["Dimensions"] = dimensions
            self.client.put_metric_data(
                Namespace=self.namespace,
                MetricData=[metric_data],
            )
        else:
            self._metrics[metric_name].append({
                "value": value,
                "unit": unit,
                "timestamp": timestamp.isoformat(),
                "dimensions": dimensions or [],
            })

    def log_event(self, level, message, context=None):
        """
        Write a structured log entry.

        Args:
            level: Log level string (INFO, WARNING, ERROR).
            message: Log message.
            context: Optional dict of additional context.
        """
        entry = {
            "level": level,
            "message": message,
            "context": context or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if self.use_aws:
            import json
            # In production, write to CloudWatch Logs
            # (simplified -- a real implementation would manage log streams)
            pass
        else:
            self._logs.append(entry)

    def create_alarm(self, alarm_name, metric_name, threshold, comparison="GreaterThanThreshold"):
        """
        Create a CloudWatch alarm for a metric.

        Args:
            alarm_name: Human-readable alarm name.
            metric_name: The metric to monitor.
            threshold: Numeric threshold that triggers the alarm.
            comparison: Comparison operator string.

        Returns:
            A dict describing the created alarm.
        """
        alarm = {
            "alarm_name": alarm_name,
            "metric_name": metric_name,
            "threshold": threshold,
            "comparison": comparison,
            "state": "OK",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        if self.use_aws:
            self.client.put_metric_alarm(
                AlarmName=alarm_name,
                Namespace=self.namespace,
                MetricName=metric_name,
                Threshold=threshold,
                ComparisonOperator=comparison,
                EvaluationPeriods=1,
                Period=300,
                Statistic="Sum",
            )
        else:
            self._alarms.append(alarm)

        return alarm

    def get_metrics_summary(self):
        """Return a summary of all recorded metrics."""
        if self.use_aws:
            return {"source": "cloudwatch", "note": "Fetch from AWS console"}
        summary = {}
        for name, points in self._metrics.items():
            values = [p["value"] for p in points]
            summary[name] = {
                "count": len(values),
                "total": sum(values),
                "average": sum(values) / len(values) if values else 0,
                "latest": points[-1] if points else None,
            }
        return summary

    def get_recent_logs(self, limit=50):
        """Return the most recent log entries."""
        return self._logs[-limit:]

    def get_status(self):
        """Return a status dictionary describing the CloudWatch connection."""
        return {
            "service": "Amazon CloudWatch",
            "status": "connected" if self.use_aws else "mock",
            "namespace": self.namespace,
            "metrics_tracked": len(self._metrics),
            "log_entries": len(self._logs),
            "alarms": len(self._alarms),
            "description": "Application monitoring, logging, and alerting",
        }
