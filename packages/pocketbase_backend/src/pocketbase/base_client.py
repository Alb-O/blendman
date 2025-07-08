"""
Base client for PocketBase API clients, providing shared auth and header logic.
"""

# pylint: disable=too-few-public-methods
from typing import Optional
import os
from .utils import load_env


class BaseClient:
    """
    Base class for PocketBase API clients.
    Handles environment loading, base URL, and auth headers.
    """

    def __init__(self, token: Optional[str] = None) -> None:
        """
        Initializes the client, loads env, and sets up state.

        Args:
            token (Optional[str]): Auth token, if available.
        """
        load_env()
        self.base_url: str = os.environ.get("POCKETBASE_URL", "http://127.0.0.1:8090")
        self.token: Optional[str] = token

    def _headers(self) -> dict[str, str]:
        """
        Returns headers for requests, including Authorization if token is set.

        Returns:
            dict[str, str]: HTTP headers.
        """
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = self.token
        return headers
