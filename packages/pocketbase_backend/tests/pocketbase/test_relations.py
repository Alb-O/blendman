"""
Unit tests for RelationsClient (link/unlink) in relations.py.
"""

import pytest
from unittest.mock import patch, MagicMock
from pocketbase.relations import RelationsClient
from pocketbase.exceptions import PocketBaseError


@pytest.fixture
def client() -> RelationsClient:
    return RelationsClient(token="test-token")


def test_link_expected(client: RelationsClient) -> None:
    with patch("pocketbase.relations.requests.patch") as mock_patch:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "abc", "friends": ["def"]}
        mock_patch.return_value = mock_resp
        result = client.link("users", "abc", "friends", "def")
        assert result == {"id": "abc", "friends": ["def"]}
        mock_patch.assert_called_once()


def test_link_invalid_args(client: RelationsClient) -> None:
    with pytest.raises(ValueError):
        client.link("", "abc", "friends", "def")
    with pytest.raises(ValueError):
        client.link("users", "", "friends", "def")
    with pytest.raises(ValueError):
        client.link("users", "abc", "", "def")
    with pytest.raises(ValueError):
        client.link("users", "abc", "friends", "")


def test_link_api_error(client: RelationsClient) -> None:
    with patch("pocketbase.relations.requests.patch") as mock_patch:
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_resp.text = "Bad Request"
        mock_patch.return_value = mock_resp
        with pytest.raises(PocketBaseError):
            client.link("users", "abc", "friends", "def")


def test_unlink_expected(client: RelationsClient) -> None:
    with (
        patch("pocketbase.relations.requests.get") as mock_get,
        patch("pocketbase.relations.requests.patch") as mock_patch,
    ):
        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.json.return_value = {"id": "abc", "friends": ["def", "ghi"]}
        mock_get.return_value = mock_get_resp
        mock_patch_resp = MagicMock()
        mock_patch_resp.status_code = 200
        mock_patch_resp.json.return_value = {"id": "abc", "friends": ["ghi"]}
        mock_patch.return_value = mock_patch_resp
        result = client.unlink("users", "abc", "friends", "def")
        assert result == {"id": "abc", "friends": ["ghi"]}
        mock_get.assert_called_once()
        mock_patch.assert_called_once()


def test_unlink_invalid_args(client: RelationsClient) -> None:
    with pytest.raises(ValueError):
        client.unlink("", "abc", "friends", "def")
    with pytest.raises(ValueError):
        client.unlink("users", "", "friends", "def")
    with pytest.raises(ValueError):
        client.unlink("users", "abc", "", "def")
    with pytest.raises(ValueError):
        client.unlink("users", "abc", "friends", "")


def test_unlink_api_error(client: RelationsClient) -> None:
    with patch("pocketbase.relations.requests.get") as mock_get:
        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 400
        mock_get_resp.text = "Bad Request"
        mock_get.return_value = mock_get_resp
        with pytest.raises(PocketBaseError):
            client.unlink("users", "abc", "friends", "def")

    with (
        patch("pocketbase.relations.requests.get") as mock_get,
        patch("pocketbase.relations.requests.patch") as mock_patch,
    ):
        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.json.return_value = {"id": "abc", "friends": ["def"]}
        mock_get.return_value = mock_get_resp
        mock_patch_resp = MagicMock()
        mock_patch_resp.status_code = 400
        mock_patch_resp.text = "Bad Patch"
        mock_patch.return_value = mock_patch_resp
        with pytest.raises(PocketBaseError):
            client.unlink("users", "abc", "friends", "def")


def test_unlink_relation_not_list(client: RelationsClient) -> None:
    with patch("pocketbase.relations.requests.get") as mock_get:
        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.json.return_value = {"id": "abc", "friends": "notalist"}
        mock_get.return_value = mock_get_resp
        with pytest.raises(PocketBaseError):
            client.unlink("users", "abc", "friends", "def")
