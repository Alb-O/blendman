"""
Tests for CollectionsClient in collections.py.
"""

from unittest.mock import patch, MagicMock
import pytest
from pocketbase.collections import CollectionsClient
from pocketbase.exceptions import PocketBaseError


def test_create_success():
    """
    Expected: create returns created record on success.
    """
    client = CollectionsClient(token="tok")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "rec1", "foo": "bar"}
    with patch("pocketbase.collections.requests.post", return_value=mock_response):
        result = client.create("test", {"foo": "bar"})
        assert result["id"] == "rec1"
        assert result["foo"] == "bar"


def test_create_invalid_args():
    """
    Edge: create with missing collection or data raises ValueError.
    """
    client = CollectionsClient()
    with pytest.raises(ValueError):
        client.create("", {"foo": "bar"})
    with pytest.raises(ValueError):
        client.create("test", {})


def test_create_api_error():
    """
    Failure: create raises PocketBaseError on API error.
    """
    client = CollectionsClient(token="tok")
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad request"
    with patch("pocketbase.collections.requests.post", return_value=mock_response):
        with pytest.raises(PocketBaseError):
            client.create("test", {"foo": "bar"})


def test_get_success():
    """
    Expected: get returns record data on success.
    """
    client = CollectionsClient(token="tok")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "rec1", "foo": "bar"}
    with patch("pocketbase.collections.requests.get", return_value=mock_response):
        result = client.get("test", "rec1")
        assert result["id"] == "rec1"


def test_get_invalid_args():
    """
    Edge: get with missing collection or record_id raises ValueError.
    """
    client = CollectionsClient()
    with pytest.raises(ValueError):
        client.get("", "rec1")
    with pytest.raises(ValueError):
        client.get("test", "")


def test_get_api_error():
    """
    Failure: get raises PocketBaseError on API error.
    """
    client = CollectionsClient(token="tok")
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not found"
    with patch("pocketbase.collections.requests.get", return_value=mock_response):
        with pytest.raises(PocketBaseError):
            client.get("test", "rec1")


def test_update_success():
    """
    Expected: update returns updated record on success.
    """
    client = CollectionsClient(token="tok")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "rec1", "foo": "baz"}
    with patch("pocketbase.collections.requests.patch", return_value=mock_response):
        result = client.update("test", "rec1", {"foo": "baz"})
        assert result["foo"] == "baz"


def test_update_invalid_args():
    """
    Edge: update with missing args raises ValueError.
    """
    client = CollectionsClient()
    with pytest.raises(ValueError):
        client.update("", "rec1", {"foo": "baz"})
    with pytest.raises(ValueError):
        client.update("test", "", {"foo": "baz"})
    with pytest.raises(ValueError):
        client.update("test", "rec1", {})


def test_update_api_error():
    """
    Failure: update raises PocketBaseError on API error.
    """
    client = CollectionsClient(token="tok")
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad request"
    with patch("pocketbase.collections.requests.patch", return_value=mock_response):
        with pytest.raises(PocketBaseError):
            client.update("test", "rec1", {"foo": "baz"})


def test_delete_success():
    """
    Expected: delete returns None on success (204).
    """
    client = CollectionsClient(token="tok")
    mock_response = MagicMock()
    mock_response.status_code = 204
    with patch("pocketbase.collections.requests.delete", return_value=mock_response):
        assert client.delete("test", "rec1") is None


def test_delete_invalid_args():
    """
    Edge: delete with missing args raises ValueError.
    """
    client = CollectionsClient()
    with pytest.raises(ValueError):
        client.delete("", "rec1")
    with pytest.raises(ValueError):
        client.delete("test", "")


def test_delete_api_error():
    """
    Failure: delete raises PocketBaseError on API error.
    """
    client = CollectionsClient(token="tok")
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad request"
    with patch("pocketbase.collections.requests.delete", return_value=mock_response):
        with pytest.raises(PocketBaseError):
            client.delete("test", "rec1")


def test_query_success():
    """
    Expected: query returns records and pagination info.
    """
    client = CollectionsClient(token="tok")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": [{"id": "rec1"}], "page": 1}
    with patch("pocketbase.collections.requests.get", return_value=mock_response):
        result = client.query("test", filters={"foo": "bar"}, page=1, per_page=10)
        assert "items" in result
        assert result["page"] == 1


def test_query_invalid_args():
    """
    Edge: query with missing collection raises ValueError.
    """
    client = CollectionsClient()
    with pytest.raises(ValueError):
        client.query("")


def test_query_api_error():
    """
    Failure: query raises PocketBaseError on API error.
    """
    client = CollectionsClient(token="tok")
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad request"
    with patch("pocketbase.collections.requests.get", return_value=mock_response):
        with pytest.raises(PocketBaseError):
            client.query("test", filters={"foo": "bar"})
