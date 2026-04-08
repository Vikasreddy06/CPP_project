"""
Amazon SNS service wrapper.
Sends push notifications for match alerts, claim updates, and system events.
Falls back to logging notifications in memory when USE_AWS is False.

Author: Vikas Reddy Amanagantti (x25178849)
"""

from datetime import datetime, timezone


class SNSService:
    """Encapsulates all interactions with Amazon Simple Notification Service."""

    def __init__(self, app=None):
        self.app = app
        self.use_aws = False
        self.client = None
        self.topic_arn = None
        # Mock notification log
        self._notifications = []
        self._subscriptions = []
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialise the service with Flask app configuration."""
        self.app = app
        self.use_aws = app.config.get("USE_AWS", False)
        self.topic_arn = app.config.get("SNS_TOPIC_ARN", "")
        self.region = app.config.get("AWS_REGION", "eu-west-1")
        if self.use_aws:
            import boto3
            self.client = boto3.client("sns", region_name=self.region)

    def publish_notification(self, subject, message, attributes=None):
        """
        Publish a notification to the configured SNS topic.

        Args:
            subject: Short subject line for the notification.
            message: Full message body.
            attributes: Optional dict of SNS message attributes.

        Returns:
            A dict with 'message_id' and 'status'.
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        if self.use_aws:
            params = {
                "TopicArn": self.topic_arn,
                "Subject": subject,
                "Message": message,
            }
            if attributes:
                params["MessageAttributes"] = {
                    k: {"DataType": "String", "StringValue": str(v)}
                    for k, v in attributes.items()
                }
            response = self.client.publish(**params)
            return {
                "message_id": response["MessageId"],
                "status": "sent",
            }
        else:
            notification = {
                "id": len(self._notifications) + 1,
                "subject": subject,
                "message": message,
                "attributes": attributes or {},
                "timestamp": timestamp,
                "status": "mock_sent",
            }
            self._notifications.append(notification)
            return {
                "message_id": f"mock-{notification['id']}",
                "status": "mock_sent",
            }

    def notify_match_found(self, lost_item, found_item, confidence):
        """Send a notification when a potential match is detected."""
        subject = "Potential Match Found for Your Lost Item"
        message = (
            f"A found item '{found_item.get('title', 'Unknown')}' may match your "
            f"lost item '{lost_item.get('title', 'Unknown')}' with "
            f"{confidence:.0%} confidence. Please review the match in the system."
        )
        return self.publish_notification(subject, message, {
            "notification_type": "match_found",
            "confidence": str(confidence),
        })

    def notify_claim_update(self, claim, new_status):
        """Send a notification when a claim status changes."""
        subject = f"Claim Status Updated: {new_status.title()}"
        message = (
            f"Your claim (ID: {claim.get('id', 'N/A')}) has been updated "
            f"to status: {new_status}."
        )
        return self.publish_notification(subject, message, {
            "notification_type": "claim_update",
            "claim_status": new_status,
        })

    def subscribe_email(self, email):
        """Subscribe an email address to the notification topic."""
        if self.use_aws:
            response = self.client.subscribe(
                TopicArn=self.topic_arn,
                Protocol="email",
                Endpoint=email,
            )
            return {"subscription_arn": response["SubscriptionArn"], "status": "pending"}
        else:
            sub = {
                "email": email,
                "status": "mock_subscribed",
                "subscription_arn": f"arn:aws:sns:local:mock:{email}",
            }
            self._subscriptions.append(sub)
            return sub

    def get_notifications(self):
        """Return all mock notifications (useful for debugging)."""
        return self._notifications

    def get_status(self):
        """Return a status dictionary describing the SNS connection."""
        return {
            "service": "Amazon SNS",
            "status": "connected" if self.use_aws else "mock",
            "topic_arn": self.topic_arn if self.use_aws else "mock-topic",
            "notifications_sent": len(self._notifications),
            "subscriptions": len(self._subscriptions),
            "description": "Push notifications for match alerts and claim updates",
        }
