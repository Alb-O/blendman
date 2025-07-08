"""
Authentication logic for PocketBase API.
"""


class AuthClient:
    """
    Handles authentication with PocketBase.
    """

    def login(self, username: str, password: str) -> str:
        """
        Logs in and returns an auth token.

        Args:
            username (str): Username or email.
            password (str): Password.

        Returns:
            str: Auth token.
        """
        raise NotImplementedError()

    def logout(self) -> None:
        """
        Logs out the current user.
        """
        raise NotImplementedError()
