"""
Tests for AuthClient in auth.py.
"""

from unittest.mock import patch, MagicMock
import pytest  # type: ignore
import requests  # type: ignore
from pocketbase.auth import AuthClient
from pocketbase.exceptions import PocketBaseError


def test_login_success():
    """
    Test expected login behavior with valid credentials.
    """
    client = AuthClient()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"token": "abc123", "record": {"id": "user1"}}
    with patch("pocketbase.auth.requests.post", return_value=mock_response):
        token = client.login("user@example.com", "password")
        assert token == "abc123"
        assert client.get_token() == "abc123"
        assert client.user == {"id": "user1"}


def test_login_failure_invalid_credentials():
    """
    Test login failure with invalid credentials (API returns 400).
    """
    client = AuthClient()
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Invalid credentials"
    with patch("pocketbase.auth.requests.post", return_value=mock_response):
        with pytest.raises(PocketBaseError) as exc:
            client.login("baduser", "badpass")
        assert "Login failed" in str(exc.value)


def test_login_http_error():
    """
    Test login failure due to network error (requests.RequestException).
    """
    client = AuthClient()

    with patch(
        "pocketbase.auth.requests.post",
        side_effect=requests.RequestException("Network down"),
    ):
        with pytest.raises(PocketBaseError) as exc:
            client.login("user", "pass")
        assert "HTTP error during login" in str(exc.value)


def test_logout_success():
    """
    Test expected logout behavior after login.
    """
    client = AuthClient()
    client.token_manager.set_token("abc123")
    client.user = {"id": "user1"}
    client.logout()
    assert client.get_token() is None
    assert client.user is None


def test_logout_not_logged_in():
    """
    Test logout failure when not logged in.
    """
    client = AuthClient()
    with pytest.raises(PocketBaseError) as exc:
        client.logout()
    assert "Not logged in" in str(exc.value)


def test_is_authenticated_valid_token():
    client = AuthClient()
    client.token_manager.set_token("tok")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    with patch("pocketbase.auth.requests.post", side_effect=[mock_resp]):
        assert client.is_authenticated()


def test_is_authenticated_invalid_token():
    client = AuthClient()
    client.token_manager.set_token("tok")
    resp1 = MagicMock()
    resp1.status_code = 401
    resp2 = MagicMock()
    resp2.status_code = 401
    with patch("pocketbase.auth.requests.post", side_effect=[resp1, resp2]):
        assert not client.is_authenticated()
