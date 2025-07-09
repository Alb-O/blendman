"""
Unit tests for MFAClient (MFA/OAuth2 logic stubs).
"""

from pocketbase.mfa import MFAClient


def test_login_with_otp_stub():
    """
    Test that login_with_otp returns None (stub by default).
    """
    mfa = MFAClient()
    assert mfa.login_with_otp("user", "otp") is None


def test_login_with_oauth2_stub():
    """
    Test that login_with_oauth2 returns None (stub by default).
    """
    mfa = MFAClient()
    assert mfa.login_with_oauth2("provider", "code", "uri") is None
