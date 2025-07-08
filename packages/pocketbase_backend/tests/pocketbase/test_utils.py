"""
Unit tests for utils.py (load_env, get_env_var).
"""

import os
import pathlib
import pytest
from pocketbase.utils import load_env, get_env_var


def test_load_env_sets_vars(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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
    monkeypatch.setenv("PB_X", "yval")
    assert get_env_var("PB_X") == "yval"


def test_get_env_var_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PB_Y", raising=False)
    assert get_env_var("PB_Y", default="zzz") == "zzz"
    assert get_env_var("PB_Y") is None
