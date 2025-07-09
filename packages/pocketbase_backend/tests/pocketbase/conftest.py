import pytest
from pocketbase.tokens import TokenManager


@pytest.fixture(autouse=True)
def reset_token():
    """Ensure global auth token is cleared between tests."""
    TokenManager().clear_token()
    yield
    TokenManager().clear_token()
