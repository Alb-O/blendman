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
    """
    Test the base exception class PocketBaseError.
    """
    with pytest.raises(PocketBaseError):
        raise PocketBaseError("base error")


def test_auth_exception():
    """
    Test the authentication exception PocketBaseAuthError.
    """
    with pytest.raises(PocketBaseAuthError):
        raise PocketBaseAuthError("auth error")
    assert issubclass(PocketBaseAuthError, PocketBaseError)


def test_not_found_exception():
    """
    Test the not found exception PocketBaseNotFoundError.
    """
    with pytest.raises(PocketBaseNotFoundError):
        raise PocketBaseNotFoundError("not found")
    assert issubclass(PocketBaseNotFoundError, PocketBaseError)


def test_validation_exception():
    """
    Test the validation exception PocketBaseValidationError.
    """
    with pytest.raises(PocketBaseValidationError):
        raise PocketBaseValidationError("validation error")
    assert issubclass(PocketBaseValidationError, PocketBaseError)


def test_server_exception():
    """
    Test the server exception PocketBaseServerError.
    """
    with pytest.raises(PocketBaseServerError):
        raise PocketBaseServerError("server error")
    assert issubclass(PocketBaseServerError, PocketBaseError)


def test_pocketbase_error_ne():
    """
    Test the __ne__ method of PocketBaseError for inequality comparison.
    """
    error1 = PocketBaseError("error 1")
    error2 = PocketBaseError("error 2")
    assert error1 != error2


def test_pocketbase_error_hash():
    """
    Test the __hash__ method of PocketBaseError for hashability.
    """
    error = PocketBaseError("error")
    assert isinstance(hash(error), int)
