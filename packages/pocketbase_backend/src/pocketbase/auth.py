"""
Authentication logic for PocketBase API.
Handles login, logout, and token management for PocketBase.
"""

from typing import Optional, Any
import os
import requests  # type: ignore
from .exceptions import PocketBaseError
from .utils import load_env


class AuthClient:
    """
    Handles authentication with PocketBase.
    Provides login, logout, and token management.
    """

    def __init__(self) -> None:
        """
        Initializes the AuthClient, loads environment variables, and sets up state.
        """
        load_env()
        self.base_url: str = os.environ.get("POCKETBASE_URL", "http://127.0.0.1:8090")
        self.token: Optional[str] = None
        self.user: Optional[dict[str, Any]] = None

    def login(self, username: str, password: str) -> str:
        """
        Logs in to PocketBase and stores the auth token.

        Args:
            username (str): Username or email.
            password (str): Password.

        Returns:
            str: Auth token.

        Raises:
            PocketBaseError: If authentication fails or API returns an error.
        """
        url = f"{self.base_url}/api/collections/users/auth-with-password"
        data = {"identity": username, "password": password}
        try:
            resp = requests.post(url, json=data, timeout=10)
            if resp.status_code != 200:
                raise PocketBaseError(f"Login failed: {resp.status_code} {resp.text}")
            result = resp.json()
            self.token = result.get("token")
            self.user = result.get("record")
            if not self.token:
                raise PocketBaseError("No token returned from PocketBase.")
            return self.token
        except requests.RequestException as e:
            raise PocketBaseError(f"HTTP error during login: {e}") from e

    def logout(self) -> None:
        """
        Logs out the current user by clearing the token and user info.

        Raises:
            PocketBaseError: If not logged in.
        """
        if not self.token:
            raise PocketBaseError("Not logged in.")
        self.token = None
        self.user = None

    def get_token(self) -> Optional[str]:
        """
        Returns the current auth token, if logged in.

        Returns:
            Optional[str]: The auth token, or None if not logged in.
        """
        return self.token
