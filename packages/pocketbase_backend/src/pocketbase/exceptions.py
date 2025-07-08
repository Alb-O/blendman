"""
Custom exceptions for PocketBase API.
"""


class PocketBaseError(Exception):
    """
    Base exception for PocketBase API errors.

    Args:
        message (str): Error message.
    """


class PocketBaseAuthError(PocketBaseError):
    """
    Raised for authentication or authorization errors.

    Args:
        message (str): Error message.
    """


class PocketBaseNotFoundError(PocketBaseError):
    """
    Raised when a requested resource is not found.

    Args:
        message (str): Error message.
    """


class PocketBaseValidationError(PocketBaseError):
    """
    Raised for validation or bad request errors.

    Args:
        message (str): Error message.
    """


class PocketBaseServerError(PocketBaseError):
    """
    Raised for server-side errors (5xx).

    Args:
        message (str): Error message.
    """
