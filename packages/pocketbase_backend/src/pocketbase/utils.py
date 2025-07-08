"""
Utility functions for PocketBase API.
"""

from dotenv import load_dotenv  # type: ignore


def load_env(dotenv_path: str | None = None) -> None:
    """
    Loads environment variables from a .env file using python-dotenv.

    Args:
        dotenv_path (str | None): Optional path to the .env file. If None, uses default search.

    Returns:
        None
    """
    if dotenv_path:
        load_dotenv(dotenv_path)
    else:
        load_dotenv()


def get_env_var(key: str, default: str | None = None) -> str | None:
    """
    Safely retrieves an environment variable.

    Args:
        key (str): The environment variable name.
        default (str | None): Default value if not set.

    Returns:
        str | None: The value of the environment variable, or default if not set.
    """
    import os

    return os.environ.get(key, default)
