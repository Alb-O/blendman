"""
Custom exceptions for PocketBase API.
"""


class PocketBaseError(Exception):
    """
    Base exception for PocketBase API errors.

    Args:
        message (str): Error message.
    """

    pass


class PocketBaseAuthError(PocketBaseError):
    """
    Raised for authentication or authorization errors.

    Args:
        message (str): Error message.
    """

    pass


class PocketBaseNotFoundError(PocketBaseError):
    """
    Raised when a requested resource is not found.

    Args:
        message (str): Error message.
    """

    pass


class PocketBaseValidationError(PocketBaseError):
    """
    Raised for validation or bad request errors.

    Args:
        message (str): Error message.
    """

    pass


class PocketBaseServerError(PocketBaseError):
    """
    Raised for server-side errors (5xx).

    Args:
        message (str): Error message.
    """

    pass
