"""
MFA and OAuth2 logic for PocketBase authentication.
Implements stubs if not enabled in PocketBase admin UI.
"""

from typing import Optional, Dict


class MFAClient:
    """
    Handles MFA and OAuth2 authentication flows for PocketBase.
    Stub methods are provided if not enabled.
    """

    def __init__(self) -> None:
        pass

    def login_with_otp(self, identity: str, otp: str) -> Optional[Dict]:
        """
        Stub for OTP login. Implement if enabled in PocketBase.

        Args:
                identity (str): Username or email.
                otp (str): One-time password.

        Returns:
                Optional[Dict]: Auth response or None if not implemented.
        """
        # Not implemented by default
        return None

    def login_with_oauth2(
        self, provider: str, code: str, redirect_uri: str
    ) -> Optional[Dict]:
        """
        Stub for OAuth2 login. Implement if enabled in PocketBase.

        Args:
                provider (str): OAuth2 provider name.
                code (str): Authorization code.
                redirect_uri (str): Redirect URI.

        Returns:
                Optional[Dict]: Auth response or None if not implemented.
        """
        # Not implemented by default
        return None
