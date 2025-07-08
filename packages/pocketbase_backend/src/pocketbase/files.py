"""
File upload and download for PocketBase.
"""

# pylint: disable=too-few-public-methods
from typing import Any


class FilesClient:
    """
    Handles file upload and download.
    """

    def upload(self, collection: str, record_id: str, file_path: str) -> dict[str, Any]:
        """
        Upload a file to a record.

        Args:
            collection (str): Collection name.
            record_id (str): Record ID.
            file_path (str): Path to file.

        Returns:
            dict: Upload result.
        """
        raise NotImplementedError()
