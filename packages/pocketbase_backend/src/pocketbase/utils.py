"""
Utility functions for PocketBase API.
"""

from dotenv import load_dotenv  # type: ignore
from typing import Callable, TypeVar


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


def load_envs(dotenv_paths: list[str] | None = None) -> None:
    """
    Loads environment variables from multiple .env files in order. Later files override earlier ones.

    Args:
        dotenv_paths (list[str] | None): List of dotenv file paths to load. If None, loads default .env.

    Returns:
        None
    """
    if dotenv_paths:
        for path in dotenv_paths:
            load_dotenv(path, override=True)
    else:
        load_dotenv()


def get_env_var(key: str, default: str | None = None) -> str | None:
    """
    Safely retrieves an environment variable as a string.

    Args:
        key (str): The environment variable name.
        default (str | None): Default value if not set.

    Returns:
        str | None: The value of the environment variable, or default if not set.
    """
    import os

    return os.environ.get(key, default)


T = TypeVar("T")


def get_env_var_typed(
    key: str,
    cast_type: Callable[[str], T],
    default: T | None = None,
    required: bool = False,
) -> T | None:
    """
    Retrieves an environment variable and casts it to a given type.

    Args:
        key (str): The environment variable name.
        default (T | None): Default value if not set.
        cast_type (Callable[[str], T]): Function to cast the string value to desired type
            (e.g., int, bool).
        required (bool): If True, raises ValueError if the variable is missing.

    Returns:
        T | None: The value of the environment variable, cast to type T, or default if not set.

    Raises:
        ValueError: If required is True and the variable is missing.
        ValueError: If casting fails.
    """
    import os

    val = os.environ.get(key)
    if val is None:
        if required:
            raise ValueError(f"Required environment variable '{key}' is missing.")
        return default
    try:
        return cast_type(val)
    except Exception as e:
        raise ValueError(
            f"Failed to cast environment variable '{key}' to {cast_type}: {e}"
        )


def require_env_var(key: str) -> str:
    """
    Retrieves a required environment variable, raising an error if missing.

    Args:
        key (str): The environment variable name.

    Returns:
        str: The value of the environment variable.

    Raises:
        ValueError: If the variable is missing.
    """
    import os

    val = os.environ.get(key)
    if val is None:
        raise ValueError(f"Required environment variable '{key}' is missing.")
    return val
