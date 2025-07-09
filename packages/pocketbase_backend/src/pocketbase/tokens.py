"""
Token management utilities for PocketBase authentication.
All tokens are managed in memory only; no disk persistence.
"""

from typing import Optional
import threading


class TokenManager:
    """Global in-memory manager for PocketBase auth tokens."""

    _token: Optional[str] = None
    _lock = threading.Lock()

    def __init__(self) -> None:  # pragma: no cover - nothing to initialize
        pass

    def set_token(self, token: str) -> None:
        """
        Set the current auth token.

        Args:
                token (str): The auth token to store.
        """
        with self._lock:
            TokenManager._token = token

    def get_token(self) -> Optional[str]:
        """
        Get the current auth token.

        Returns:
                Optional[str]: The current auth token, or None if not set.
        """
        with self._lock:
            return TokenManager._token

    def clear_token(self) -> None:
        """
        Clear the current auth token from memory.
        """
        with self._lock:
            TokenManager._token = None
