# pylint: disable=unused-argument
"""
Unit tests for utils.py (load_env, get_env_var).
"""

import os
import pathlib
import pytest
from pocketbase.utils import (
    load_env,
    load_envs,
    get_env_var,
    get_env_var_typed,
    require_env_var,
)


def test_load_env_sets_vars(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Test that load_env sets environment variables from a .env file.

    Args:
        tmp_path (pathlib.Path): Temporary directory for test files.
        monkeypatch (pytest.MonkeyPatch): Pytest monkeypatch fixture.
    """
    # Create a .env file
    env_file = tmp_path / ".env"
    env_file.write_text("POCKETBASE_URL=http://test:1234\nFOO=bar\n")
    # Unset vars if present
    os.environ.pop("POCKETBASE_URL", None)
    os.environ.pop("FOO", None)
    load_env(str(env_file))
    assert os.environ["POCKETBASE_URL"] == "http://test:1234"
    assert os.environ["FOO"] == "bar"


def test_get_env_var_existing(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test get_env_var returns the value for an existing environment variable.

    Args:
        monkeypatch (pytest.MonkeyPatch): Pytest monkeypatch fixture.
    """
    monkeypatch.setenv("PB_X", "yval")
    assert get_env_var("PB_X") == "yval"


def test_get_env_var_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test get_env_var returns the default value if the variable is missing.

    Args:
        monkeypatch (pytest.MonkeyPatch): Pytest monkeypatch fixture.
    """
    monkeypatch.delenv("PB_Y", raising=False)
    assert get_env_var("PB_Y", default="zzz") == "zzz"
    assert get_env_var("PB_Y") is None


def test_load_envs_multiple(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Test that load_envs loads and overrides environment variables from multiple files.

    Args:
        tmp_path (pathlib.Path): Temporary directory for test files.
        monkeypatch (pytest.MonkeyPatch): Pytest monkeypatch fixture.
    """
    # .env sets FOO=bar, .env.local overrides FOO=baz
    env1 = tmp_path / ".env"
    env2 = tmp_path / ".env.local"
    env1.write_text("FOO=bar\nBAR=1\n")
    env2.write_text("FOO=baz\nBAR=2\n")
    monkeypatch.delenv("FOO", raising=False)
    monkeypatch.delenv("BAR", raising=False)
    load_envs([str(env1), str(env2)])
    assert os.environ["FOO"] == "baz"
    assert os.environ["BAR"] == "2"


def test_get_env_var_typed_int(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test get_env_var_typed returns an int when requested.

    Args:
        monkeypatch (pytest.MonkeyPatch): Pytest monkeypatch fixture.
    """
    monkeypatch.setenv("PB_INT", "42")
    val = get_env_var_typed("PB_INT", int)
    assert val == 42


def test_get_env_var_typed_bool(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test get_env_var_typed returns a boolean when requested.

    Args:
        monkeypatch (pytest.MonkeyPatch): Pytest monkeypatch fixture.
    """
    monkeypatch.setenv("PB_BOOL", "1")
    val = get_env_var_typed("PB_BOOL", lambda v: v == "1")
    assert val is True


def test_get_env_var_typed_required(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test get_env_var_typed raises ValueError if required variable is missing.

    Args:
        monkeypatch (pytest.MonkeyPatch): Pytest monkeypatch fixture.
    """
    monkeypatch.delenv("PB_REQ", raising=False)
    with pytest.raises(ValueError):
        get_env_var_typed("PB_REQ", str, required=True)


def test_get_env_var_typed_cast_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test get_env_var_typed raises ValueError if cast fails.

    Args:
        monkeypatch (pytest.MonkeyPatch): Pytest monkeypatch fixture.
    """
    monkeypatch.setenv("PB_BAD", "notanint")
    with pytest.raises(ValueError):
        get_env_var_typed("PB_BAD", int)


def test_require_env_var_present(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test require_env_var returns the value if present.

    Args:
        monkeypatch (pytest.MonkeyPatch): Pytest monkeypatch fixture.
    """
    monkeypatch.setenv("PB_REQ2", "abc")
    assert require_env_var("PB_REQ2") == "abc"


def test_require_env_var_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test require_env_var raises ValueError if variable is missing.

    Args:
        monkeypatch (pytest.MonkeyPatch): Pytest monkeypatch fixture.
    """
    monkeypatch.delenv("PB_REQ3", raising=False)
    with pytest.raises(ValueError):
        require_env_var("PB_REQ3")
