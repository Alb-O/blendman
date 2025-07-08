"""
Relations handling for PocketBase records.
"""

from typing import Any


class RelationsClient:
    """
    Handles relations between PocketBase records.
    """

    def link(
        self, collection: str, record_id: str, related_collection: str, related_id: str
    ) -> dict[str, Any]:
        """
        Link two records by relation.

        Args:
            collection (str): Source collection.
            record_id (str): Source record ID.
            related_collection (str): Related collection.
            related_id (str): Related record ID.

        Returns:
            dict: Result of linking.
        """
        raise NotImplementedError()
