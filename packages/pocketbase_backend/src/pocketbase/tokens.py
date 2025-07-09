"""
Token management utilities for PocketBase authentication.
All tokens are managed in memory only; no disk persistence.
"""

from typing import Optional
import threading


class TokenManager:
    """
    Manages PocketBase auth tokens securely in memory.
    Thread-safe for concurrent access.
    """

    def __init__(self) -> None:
        self._token: Optional[str] = None
        self._lock = threading.Lock()

    def set_token(self, token: str) -> None:
        """
        Set the current auth token.

        Args:
                token (str): The auth token to store.
        """
        with self._lock:
            self._token = token

    def get_token(self) -> Optional[str]:
        """
        Get the current auth token.

        Returns:
                Optional[str]: The current auth token, or None if not set.
        """
        with self._lock:
            return self._token

    def clear_token(self) -> None:
        """
        Clear the current auth token from memory.
        """
        with self._lock:
            self._token = None
