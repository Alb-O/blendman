"""
CRUD and query operations for PocketBase collections.
"""

from typing import Any, Optional
import requests  # type: ignore
from .exceptions import PocketBaseError
from .base_client import BaseClient


class CollectionsClient(BaseClient):
    """
    Handles CRUD and query for PocketBase collections.
    """

    def create(self, collection: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        Create a new record in a collection.

        Args:
            collection (str): Collection name.
            data (dict): Record data.

        Returns:
            dict: Created record.

        Raises:
            PocketBaseError: If API returns an error.
            ValueError: If arguments are invalid.
        """
        if not collection or not data:
            raise ValueError("Collection name and data dict required.")
        url = f"{self.base_url}/api/collections/{collection}/records"
        try:
            resp = requests.post(url, json=data, headers=self._headers(), timeout=10)
            if resp.status_code != 200:
                raise PocketBaseError(f"Create failed: {resp.status_code} {resp.text}")
            return resp.json()
        except requests.RequestException as e:
            raise PocketBaseError(f"HTTP error during create: {e}") from e

    def get(self, collection: str, record_id: str) -> dict[str, Any]:
        """
        Get a record by ID.

        Args:
            collection (str): Collection name.
            record_id (str): Record ID.

        Returns:
            dict: Record data.

        Raises:
            PocketBaseError: If API returns an error.
            ValueError: If arguments are invalid.
        """
        if not collection or not record_id:
            raise ValueError("Collection and record_id required.")
        url = f"{self.base_url}/api/collections/{collection}/records/{record_id}"
        try:
            resp = requests.get(url, headers=self._headers(), timeout=10)
            if resp.status_code != 200:
                raise PocketBaseError(f"Get failed: {resp.status_code} {resp.text}")
            return resp.json()
        except requests.RequestException as e:
            raise PocketBaseError(f"HTTP error during get: {e}") from e

    def update(
        self, collection: str, record_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Update a record in a collection.

        Args:
            collection (str): Collection name.
            record_id (str): Record ID.
            data (dict): Updated data.

        Returns:
            dict: Updated record.

        Raises:
            PocketBaseError: If API returns an error.
            ValueError: If arguments are invalid.
        """
        if not collection or not record_id or not data:
            raise ValueError("Collection, record_id, and data dict required.")
        url = f"{self.base_url}/api/collections/{collection}/records/{record_id}"
        try:
            resp = requests.patch(url, json=data, headers=self._headers(), timeout=10)
            if resp.status_code != 200:
                raise PocketBaseError(f"Update failed: {resp.status_code} {resp.text}")
            return resp.json()
        except requests.RequestException as e:
            raise PocketBaseError(f"HTTP error during update: {e}") from e

    def delete(self, collection: str, record_id: str) -> None:
        """
        Delete a record from a collection.

        Args:
            collection (str): Collection name.
            record_id (str): Record ID.

        Raises:
            PocketBaseError: If API returns an error.
            ValueError: If arguments are invalid.
        """
        if not collection or not record_id:
            raise ValueError("Collection and record_id required.")
        url = f"{self.base_url}/api/collections/{collection}/records/{record_id}"
        try:
            resp = requests.delete(url, headers=self._headers(), timeout=10)
            if resp.status_code != 204:
                raise PocketBaseError(f"Delete failed: {resp.status_code} {resp.text}")
        except requests.RequestException as e:
            raise PocketBaseError(f"HTTP error during delete: {e}") from e

    def query(
        self,
        collection: str,
        filters: Optional[dict[str, Any]] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict[str, Any]:
        """
        Query records in a collection with optional filters and pagination.

        Args:
            collection (str): Collection name.
            filters (Optional[dict]): Query filters (field: value).
            page (int): Page number (1-based).
            per_page (int): Records per page.

        Returns:
            dict: Query result (records, pagination info).

        Raises:
            PocketBaseError: If API returns an error.
            ValueError: If arguments are invalid.
        """
        if not collection:
            raise ValueError("Collection required.")
        url = f"{self.base_url}/api/collections/{collection}/records"
        params: dict[str, Any] = {"page": page, "perPage": per_page}
        if filters:
            # PocketBase expects filter string, e.g. 'field1="foo" && field2>10'
            filter_str = " && ".join(
                f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}"
                for k, v in filters.items()
            )
            params["filter"] = filter_str
        try:
            resp = requests.get(url, headers=self._headers(), params=params, timeout=10)
            if resp.status_code != 200:
                raise PocketBaseError(f"Query failed: {resp.status_code} {resp.text}")
            return resp.json()
        except requests.RequestException as e:
            raise PocketBaseError(f"HTTP error during query: {e}") from e
