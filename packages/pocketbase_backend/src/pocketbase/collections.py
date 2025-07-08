"""
CRUD operations for PocketBase collections.
"""

from typing import Any


class CollectionsClient:
    """
    Handles CRUD for PocketBase collections.
    """

    def create(self, collection: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        Create a new record in a collection.

        Args:
            collection (str): Collection name.
            data (dict): Record data.

        Returns:
            dict: Created record.
        """
        raise NotImplementedError()

    def get(self, collection: str, record_id: str) -> dict[str, Any]:
        """
        Get a record by ID.

        Args:
            collection (str): Collection name.
            record_id (str): Record ID.

        Returns:
            dict: Record data.
        """
        raise NotImplementedError()
