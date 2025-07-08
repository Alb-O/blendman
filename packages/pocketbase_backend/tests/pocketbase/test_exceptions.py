"""
Unit tests for custom exceptions in exceptions.py.
"""

import pytest
from pocketbase.exceptions import (
    PocketBaseError,
    PocketBaseAuthError,
    PocketBaseNotFoundError,
    PocketBaseValidationError,
    PocketBaseServerError,
)


def test_base_exception():
    with pytest.raises(PocketBaseError):
        raise PocketBaseError("base error")


def test_auth_exception():
    with pytest.raises(PocketBaseAuthError):
        raise PocketBaseAuthError("auth error")
    assert issubclass(PocketBaseAuthError, PocketBaseError)


def test_not_found_exception():
    with pytest.raises(PocketBaseNotFoundError):
        raise PocketBaseNotFoundError("not found")
    assert issubclass(PocketBaseNotFoundError, PocketBaseError)


def test_validation_exception():
    with pytest.raises(PocketBaseValidationError):
        raise PocketBaseValidationError("validation error")
    assert issubclass(PocketBaseValidationError, PocketBaseError)


def test_server_exception():
    with pytest.raises(PocketBaseServerError):
        raise PocketBaseServerError("server error")
    assert issubclass(PocketBaseServerError, PocketBaseError)
