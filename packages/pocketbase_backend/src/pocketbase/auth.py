"""
Authentication logic for PocketBase API.
Handles login, logout, token management, OTP, OAuth2, MFA, and impersonation.
"""

import logging
import os
from typing import Optional, Any
import requests  # type: ignore
from .exceptions import PocketBaseAuthError
from .utils import load_env
from .tokens import TokenManager
from .mfa import MFAClient


class AuthClient:
    """
    Handles authentication with PocketBase.
    Provides login, logout, token management, OTP, OAuth2, MFA, and impersonation.
    """

    def __init__(self) -> None:
        """
        Initializes the AuthClient, loads environment variables, and sets up state.
        """
        load_env()
        self.base_url: str = os.environ.get("POCKETBASE_URL", "http://127.0.0.1:8090")
        self.token_manager = TokenManager()
        self.mfa_client = MFAClient()
        self.user: Optional[dict[str, Any]] = None
        self.logger = logging.getLogger("AuthClient")

    def login(self, username: str, password: str) -> str:
        """
        Logs in to PocketBase using password authentication.

        Args:
            username (str): Username or email.
            password (str): Password.

        Returns:
            str: Auth token.

        Raises:
            PocketBaseError: If authentication fails or API returns an error.
        """
        # Always use 'identity' for both admin and user endpoints
        url = f"{self.base_url}/api/collections/_superusers/auth-with-password"
        data = {"identity": username, "password": password}
        try:
            resp = requests.post(url, json=data, timeout=10)
            if resp.status_code != 200:
                raise PocketBaseAuthError(
                    f"Login failed: {resp.status_code} {resp.text}"
                )
            result = resp.json()
            token = result.get("token")
            self.user = result.get("record")
            if not token:
                raise PocketBaseAuthError("No token returned from PocketBase.")
            self.token_manager.set_token(token)
            return token
        except requests.RequestException as e:
            self.logger.error("HTTP error during login: %s", e)
            raise PocketBaseAuthError(f"HTTP error during login: {e}") from e

    def login_with_otp(self, identity: str, otp: str) -> Optional[str]:
        """
        Logs in using OTP (if enabled in PocketBase).

        Args:
            identity (str): Username or email.
            otp (str): One-time password.

        Returns:
            Optional[str]: Auth token or None if not implemented.
        """
        result = self.mfa_client.login_with_otp(identity, otp) or {}
        if "token" not in result:
            return None
        self.token_manager.set_token(result["token"])
        self.user = result.get("record")
        return result["token"]

    def login_with_oauth2(
        self, provider: str, code: str, redirect_uri: str
    ) -> Optional[str]:
        """
        Logs in using OAuth2 (if enabled in PocketBase).

        Args:
            provider (str): OAuth2 provider name.
            code (str): Authorization code.
            redirect_uri (str): Redirect URI.

        Returns:
            Optional[str]: Auth token or None if not implemented.
        """
        result = self.mfa_client.login_with_oauth2(provider, code, redirect_uri) or {}
        if "token" not in result:
            return None
        self.token_manager.set_token(result["token"])
        self.user = result.get("record")
        return result["token"]

    def impersonate(self, user_id: str, superuser_token: Optional[str] = None) -> str:
        """
        Impersonates another user using a superuser token.

        Args:
            user_id (str): The user ID to impersonate.
            superuser_token (Optional[str]): Superuser token (from env if not provided).

        Returns:
            str: Impersonation token.

        Raises:
            PocketBaseAuthError: If impersonation fails.
        """
        token = superuser_token or os.environ.get("POCKETBASE_SUPERUSER_TOKEN")
        if not token:
            raise PocketBaseAuthError("Superuser token required for impersonation.")
        url = f"{self.base_url}/api/collections/users/impersonate/{user_id}"
        headers = {"Authorization": token}
        try:
            resp = requests.post(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                raise PocketBaseAuthError(
                    f"Impersonation failed: {resp.status_code} {resp.text}"
                )
            result = resp.json()
            imp_token = result.get("token")
            if not imp_token:
                raise PocketBaseAuthError("No token returned from impersonation.")
            self.token_manager.set_token(imp_token)
            self.user = result.get("record")
            return imp_token
        except requests.RequestException as e:
            self.logger.error("HTTP error during impersonation: %s", e)
            raise PocketBaseAuthError(f"HTTP error during impersonation: {e}") from e

    def refresh_token(self) -> str:
        """
        Refreshes the current auth token using /auth-refresh endpoint.

        Returns:
            str: New auth token.

        Raises:
            PocketBaseAuthError: If refresh fails.
        """
        token = self.token_manager.get_token()
        if not token:
            raise PocketBaseAuthError("No token to refresh.")
        url = f"{self.base_url}/api/collections/users/auth-refresh"
        headers = {"Authorization": token}
        try:
            resp = requests.post(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                raise PocketBaseAuthError(
                    f"Token refresh failed: {resp.status_code} {resp.text}"
                )
            result = resp.json()
            new_token = result.get("token")
            if not new_token:
                raise PocketBaseAuthError("No token returned from refresh.")
            self.token_manager.set_token(new_token)
            return new_token
        except requests.RequestException as e:
            self.logger.error("HTTP error during token refresh: %s", e)
            raise PocketBaseAuthError(f"HTTP error during token refresh: {e}") from e

    def is_authenticated(self) -> bool:
        """Check if the current auth token is valid via auth-refresh."""
        token = self.token_manager.get_token()
        if not token:
            return False
        url = f"{self.base_url}/api/collections/users/auth-refresh"
        try:
            resp = requests.post(
                url,
                headers={"Authorization": token},
                timeout=5,
            )
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def logout(self) -> None:
        """
        Logs out the current user by clearing the token and user info.

        Raises:
            PocketBaseAuthError: If not logged in.
        """
        if not self.token_manager.get_token():
            raise PocketBaseAuthError("Not logged in.")
        self.token_manager.clear_token()
        self.user = None

    def get_token(self) -> Optional[str]:
        """
        Returns the current auth token, if logged in.

        Returns:
            Optional[str]: The auth token, or None if not logged in.
        """
        return self.token_manager.get_token()
