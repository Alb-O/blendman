"""
Relations operations for PocketBase records (link/unlink).
"""

from typing import Any
import requests  # type: ignore
from .exceptions import PocketBaseError
from .base_client import BaseClient


class RelationsClient(BaseClient):
    """
    Handles linking and unlinking records in PocketBase collections.
    """

    def link(
        self,
        collection: str,
        record_id: str,
        related_collection: str,
        related_id: str,
    ) -> dict[str, Any]:
        """
        Link a record to another record via a relation field.

        Args:
            collection (str): Source collection name.
            record_id (str): Source record ID.
            related_collection (str): Related collection name.
            related_id (str): Related record ID.

        Returns:
            dict: Updated record data.

        Raises:
            PocketBaseError: If API returns an error.
            ValueError: If arguments are invalid.
        """
        if not all([collection, record_id, related_collection, related_id]):
            raise ValueError("All arguments are required.")
        # PocketBase expects the relation field to be updated with the related_id
        # We'll PATCH the source record's relation field (named after related_collection)
        url = f"{self.base_url}/api/collections/{collection}/records/{record_id}"
        data = {related_collection: [related_id]}
        try:
            resp = requests.patch(url, json=data, headers=self._headers(), timeout=10)
            if resp.status_code != 200:
                raise PocketBaseError(f"Link failed: {resp.status_code} {resp.text}")
            return resp.json()
        except requests.RequestException as e:
            raise PocketBaseError(f"HTTP error during link: {e}") from e

    def unlink(
        self,
        collection: str,
        record_id: str,
        related_collection: str,
        related_id: str,
    ) -> dict[str, Any]:
        """
        Unlink a record from another record via a relation field.

        Args:
            collection (str): Source collection name.
            record_id (str): Source record ID.
            related_collection (str): Related collection name.
            related_id (str): Related record ID.

        Returns:
            dict: Updated record data.

        Raises:
            PocketBaseError: If API returns an error.
            ValueError: If arguments are invalid.
        """
        if not all([collection, record_id, related_collection, related_id]):
            raise ValueError("All arguments are required.")
        url = f"{self.base_url}/api/collections/{collection}/records/{record_id}"
        # To unlink, fetch the current relation list, remove related_id, and PATCH
        try:
            get_resp = requests.get(url, headers=self._headers(), timeout=10)
            if get_resp.status_code != 200:
                raise PocketBaseError(
                    f"Unlink fetch failed: {get_resp.status_code} {get_resp.text}"
                )
            record = get_resp.json()
            current_rel_raw = record.get(related_collection, [])
            if not isinstance(current_rel_raw, list):
                raise PocketBaseError(
                    f"Relation field '{related_collection}' is not a list."
                )
            # Assume all relation IDs are strings
            current_rel: list[str] = [str(rid) for rid in current_rel_raw]  # type: ignore
            updated_rel: list[str] = [rid for rid in current_rel if rid != related_id]
            patch_data: dict[str, list[str]] = {related_collection: updated_rel}
            patch_resp = requests.patch(
                url, json=patch_data, headers=self._headers(), timeout=10
            )
            if patch_resp.status_code != 200:
                raise PocketBaseError(
                    f"Unlink failed: {patch_resp.status_code} {patch_resp.text}"
                )
            return patch_resp.json()
        except requests.RequestException as e:
            raise PocketBaseError(f"HTTP error during unlink: {e}") from e
