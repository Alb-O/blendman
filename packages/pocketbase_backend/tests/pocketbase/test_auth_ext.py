"""
Tests for new AuthClient features: OTP, OAuth2, MFA, impersonation, and token refresh.
"""

from unittest.mock import patch, MagicMock
import pytest  # type: ignore
from pocketbase.auth import AuthClient
from pocketbase.exceptions import PocketBaseAuthError


def test_login_with_otp_stub():
    """
    Test OTP login returns None (stub by default).
    """
    client = AuthClient()
    assert client.login_with_otp("user", "otpcode") is None


def test_login_with_oauth2_stub():
    """
    Test OAuth2 login returns None (stub by default).
    """
    client = AuthClient()
    assert client.login_with_oauth2("provider", "code", "uri") is None


def test_impersonate_no_token():
    """
    Test impersonation fails if no superuser token is set.
    """
    client = AuthClient()
    with pytest.raises(PocketBaseAuthError):
        client.impersonate("user_id", superuser_token=None)


def test_impersonate_success():
    """
    Test successful impersonation returns token and sets user.
    """
    client = AuthClient()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "token": "imp_token",
        "record": {"id": "imp_user"},
    }
    with patch("pocketbase.auth.requests.post", return_value=mock_response):
        token = client.impersonate("user_id", superuser_token="super_token")
        assert token == "imp_token"
        assert client.get_token() == "imp_token"
        assert client.user == {"id": "imp_user"}


def test_refresh_token_success():
    """
    Test successful token refresh updates token.
    """
    client = AuthClient()
    client.token_manager.set_token("old_token")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"token": "new_token"}
    with patch("pocketbase.auth.requests.post", return_value=mock_response):
        token = client.refresh_token()
        assert token == "new_token"
        assert client.get_token() == "new_token"


def test_refresh_token_no_token():
    """
    Test token refresh fails if no token is set.
    """
    client = AuthClient()
    with pytest.raises(PocketBaseAuthError):
        client.refresh_token()
