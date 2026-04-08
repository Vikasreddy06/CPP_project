"""
Amazon DynamoDB service wrapper.
Provides CRUD helpers for items, claims, users, and matches stored in DynamoDB.
Falls back to an in-memory store when USE_AWS is False.

Author: Vikas Reddy Amanagantti (x25178849)
"""

import uuid
from datetime import datetime, timezone


class DynamoDBService:
    """Encapsulates all interactions with Amazon DynamoDB."""

    def __init__(self, app=None):
        self.app = app
        self.use_aws = False
        self.client = None
        # In-memory mock tables keyed by table name, then by item id
        self._mock_tables = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialise the service with Flask app configuration."""
        self.app = app
        self.use_aws = app.config.get("USE_AWS", False)
        self.region = app.config.get("AWS_REGION", "eu-west-1")
        self.table_prefix = app.config.get("DYNAMODB_TABLE_PREFIX", "campuslf_")
        if self.use_aws:
            import boto3
            self.client = boto3.resource("dynamodb", region_name=self.region)

    # ------------------------------------------------------------------
    # Generic helpers
    # ------------------------------------------------------------------

    def _table_name(self, entity):
        """Return the full DynamoDB table name for an entity type."""
        return f"{self.table_prefix}{entity}"

    def _ensure_mock_table(self, table):
        """Ensure the in-memory mock table dict exists."""
        if table not in self._mock_tables:
            self._mock_tables[table] = {}

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    def put_item(self, entity, item_data):
        """
        Insert or replace an item in the specified entity table.

        Args:
            entity: Table/entity name (e.g. 'items', 'users').
            item_data: Dictionary of attributes to store.

        Returns:
            The stored item dictionary including its id.
        """
        table = self._table_name(entity)
        if "id" not in item_data:
            item_data["id"] = str(uuid.uuid4())
        item_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        if self.use_aws:
            dynamo_table = self.client.Table(table)
            dynamo_table.put_item(Item=item_data)
        else:
            self._ensure_mock_table(table)
            self._mock_tables[table][item_data["id"]] = item_data

        return item_data

    def get_item(self, entity, item_id):
        """
        Retrieve a single item by its id.

        Args:
            entity: Table/entity name.
            item_id: The unique identifier of the item.

        Returns:
            The item dictionary or None if not found.
        """
        table = self._table_name(entity)
        if self.use_aws:
            dynamo_table = self.client.Table(table)
            response = dynamo_table.get_item(Key={"id": str(item_id)})
            return response.get("Item")
        else:
            self._ensure_mock_table(table)
            return self._mock_tables[table].get(str(item_id))

    def get_all(self, entity):
        """
        Retrieve every item in the specified entity table.

        Args:
            entity: Table/entity name.

        Returns:
            A list of item dictionaries.
        """
        table = self._table_name(entity)
        if self.use_aws:
            dynamo_table = self.client.Table(table)
            response = dynamo_table.scan()
            return response.get("Items", [])
        else:
            self._ensure_mock_table(table)
            return list(self._mock_tables[table].values())

    def update_item(self, entity, item_id, updates):
        """
        Merge updates into an existing item.

        Args:
            entity: Table/entity name.
            item_id: The unique identifier of the item.
            updates: Dictionary of fields to update.

        Returns:
            The updated item dictionary or None if not found.
        """
        table = self._table_name(entity)
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()

        if self.use_aws:
            dynamo_table = self.client.Table(table)
            expr_parts, attr_values, attr_names = [], {}, {}
            for i, (key, val) in enumerate(updates.items()):
                placeholder = f":v{i}"
                name_ph = f"#n{i}"
                expr_parts.append(f"{name_ph} = {placeholder}")
                attr_values[placeholder] = val
                attr_names[name_ph] = key
            response = dynamo_table.update_item(
                Key={"id": str(item_id)},
                UpdateExpression="SET " + ", ".join(expr_parts),
                ExpressionAttributeValues=attr_values,
                ExpressionAttributeNames=attr_names,
                ReturnValues="ALL_NEW",
            )
            return response.get("Attributes")
        else:
            self._ensure_mock_table(table)
            item = self._mock_tables[table].get(str(item_id))
            if item is None:
                return None
            item.update(updates)
            return item

    def delete_item(self, entity, item_id):
        """
        Delete an item by its id.

        Args:
            entity: Table/entity name.
            item_id: The unique identifier of the item.

        Returns:
            True if the item existed and was deleted, False otherwise.
        """
        table = self._table_name(entity)
        if self.use_aws:
            dynamo_table = self.client.Table(table)
            dynamo_table.delete_item(Key={"id": str(item_id)})
            return True
        else:
            self._ensure_mock_table(table)
            return self._mock_tables[table].pop(str(item_id), None) is not None

    def query_by_field(self, entity, field, value):
        """
        Return all items where *field* equals *value* (scan-based).

        Args:
            entity: Table/entity name.
            field: The attribute name to filter on.
            value: The expected value.

        Returns:
            A list of matching item dictionaries.
        """
        all_items = self.get_all(entity)
        return [item for item in all_items if item.get(field) == value]

    def get_status(self):
        """Return a status dictionary describing the DynamoDB connection."""
        return {
            "service": "Amazon DynamoDB",
            "status": "connected" if self.use_aws else "mock",
            "region": self.region if self.use_aws else "local",
            "tables": list(self._mock_tables.keys()) if not self.use_aws else [],
            "description": "NoSQL database for storing items, claims, users, and matches",
        }
