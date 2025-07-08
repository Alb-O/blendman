"""
Utility functions for PocketBase API.
"""

from dotenv import load_dotenv  # type: ignore


def load_env() -> None:
    """
    Loads environment variables from a .env file.
    """
    load_dotenv()
