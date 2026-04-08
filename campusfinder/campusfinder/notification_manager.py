"""
NotificationManager -- notification rules engine, channel preferences,
alert batching, and urgency levels for the Smart Campus Lost & Found System.

Author: Vikas Reddy Amanagantti (x25178849)
"""

from datetime import datetime, timezone
from collections import defaultdict


class NotificationManager:
    """
    Manages notification rules, user channel preferences, urgency levels,
    and batching logic for sending alerts about matches and claims.
    """

    # Urgency levels (higher number = more urgent)
    URGENCY_LEVELS = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }

    # Available notification channels
    CHANNELS = ("email", "sms", "push", "in_app")

    def __init__(self):
        """Initialise with empty notification queue and preferences."""
        self._queue = []
        self._sent = []
        self._user_preferences = {}  # user_id -> {channels: [...], min_urgency: str}
        self._rules = []
        self._batch_buffer = defaultdict(list)

    # ------------------------------------------------------------------
    # User preferences
    # ------------------------------------------------------------------

    def set_user_preferences(self, user_id, channels=None, min_urgency="low"):
        """
        Set notification preferences for a user.

        Args:
            user_id: Unique user identifier.
            channels: List of channel strings the user wants to receive.
            min_urgency: Minimum urgency level for notifications.
        """
        if channels is None:
            channels = ["email", "in_app"]
        valid_channels = [c for c in channels if c in self.CHANNELS]
        self._user_preferences[user_id] = {
            "channels": valid_channels,
            "min_urgency": min_urgency,
        }

    def get_user_preferences(self, user_id):
        """Return preferences for a user, or sensible defaults."""
        return self._user_preferences.get(user_id, {
            "channels": ["email", "in_app"],
            "min_urgency": "low",
        })

    # ------------------------------------------------------------------
    # Notification rules
    # ------------------------------------------------------------------

    def add_rule(self, event_type, urgency, template):
        """
        Register a notification rule that maps an event type to an
        urgency level and message template.

        Args:
            event_type: String like 'match_found', 'claim_approved'.
            urgency: Urgency level string.
            template: Message template string with {placeholders}.
        """
        self._rules.append({
            "event_type": event_type,
            "urgency": urgency,
            "template": template,
        })

    def get_rules(self):
        """Return all registered notification rules."""
        return list(self._rules)

    def _find_rule(self, event_type):
        """Find the first rule matching the event type."""
        for rule in self._rules:
            if rule["event_type"] == event_type:
                return rule
        return None

    # ------------------------------------------------------------------
    # Creating and sending notifications
    # ------------------------------------------------------------------

    def create_notification(self, user_id, event_type, context=None):
        """
        Create a notification based on rules and user preferences.

        Args:
            user_id: Target user.
            event_type: The event that triggered this notification.
            context: dict of values to fill template placeholders.

        Returns:
            The notification dict, or None if filtered out by preferences.
        """
        context = context or {}
        rule = self._find_rule(event_type)

        if rule:
            urgency = rule["urgency"]
            try:
                message = rule["template"].format(**context)
            except KeyError:
                message = rule["template"]
        else:
            urgency = "medium"
            message = f"Notification: {event_type}"

        prefs = self.get_user_preferences(user_id)
        min_level = self.URGENCY_LEVELS.get(prefs["min_urgency"], 1)
        current_level = self.URGENCY_LEVELS.get(urgency, 2)

        if current_level < min_level:
            return None  # User does not want low-urgency notifications

        notification = {
            "id": len(self._queue) + len(self._sent) + 1,
            "user_id": user_id,
            "event_type": event_type,
            "message": message,
            "urgency": urgency,
            "channels": prefs["channels"],
            "status": "queued",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._queue.append(notification)
        return notification

    def send_pending(self):
        """
        Process and send all queued notifications.

        Returns:
            The number of notifications sent.
        """
        count = 0
        while self._queue:
            notif = self._queue.pop(0)
            notif["status"] = "sent"
            notif["sent_at"] = datetime.now(timezone.utc).isoformat()
            self._sent.append(notif)
            count += 1
        return count

    # ------------------------------------------------------------------
    # Batching
    # ------------------------------------------------------------------

    def add_to_batch(self, user_id, notification):
        """Add a notification to the batch buffer for a user."""
        self._batch_buffer[user_id].append(notification)

    def flush_batch(self, user_id):
        """
        Flush all batched notifications for a user into a single
        summary notification.

        Args:
            user_id: The user whose batch to flush.

        Returns:
            A summary notification dict, or None if buffer was empty.
        """
        buffer = self._batch_buffer.get(user_id, [])
        if not buffer:
            return None

        summary_message = f"You have {len(buffer)} new notifications:\n"
        for notif in buffer:
            summary_message += f"  - {notif.get('message', 'N/A')}\n"

        summary = {
            "id": len(self._sent) + len(self._queue) + 1,
            "user_id": user_id,
            "event_type": "batch_summary",
            "message": summary_message.strip(),
            "urgency": "medium",
            "channels": self.get_user_preferences(user_id)["channels"],
            "status": "sent",
            "batched_count": len(buffer),
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }
        self._sent.append(summary)
        self._batch_buffer[user_id] = []
        return summary

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_sent_notifications(self, user_id=None):
        """Return sent notifications, optionally filtered by user."""
        if user_id:
            return [n for n in self._sent if n["user_id"] == user_id]
        return list(self._sent)

    def get_queue_size(self):
        """Return the number of notifications waiting to be sent."""
        return len(self._queue)

    def get_notification_stats(self):
        """Return aggregate notification statistics."""
        urgency_counts = defaultdict(int)
        for n in self._sent:
            urgency_counts[n["urgency"]] += 1
        return {
            "total_sent": len(self._sent),
            "queued": len(self._queue),
            "by_urgency": dict(urgency_counts),
        }
