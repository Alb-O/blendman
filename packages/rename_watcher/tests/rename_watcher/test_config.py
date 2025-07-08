"""
Unit tests for get_config in config.py.
"""

import importlib
import sys
import pytest
from pytest import MonkeyPatch
from types import ModuleType
import rename_watcher.config as config_mod_type


# Patch environment for test isolation
def reload_config_module() -> ModuleType:
    if "rename_watcher.config" in sys.modules:
        del sys.modules["rename_watcher.config"]
    return importlib.import_module("rename_watcher.config")


def test_get_config_expected(monkeypatch: MonkeyPatch) -> None:
    """
    Test get_config returns expected config from environment (expected use).
    """
    monkeypatch.setenv("WATCHER_TIMEOUT", "3.5")
    monkeypatch.setenv("WATCHER_POLL_INTERVAL", "2.0")
    monkeypatch.setenv("WATCHER_IGNORE_PATTERNS", ".git,.env,.cache")
    config_mod = reload_config_module()
    cfg: config_mod_type.ConfigDict = config_mod.get_config()  # type: ignore[attr-defined]
    assert cfg["timeout"] == 3.5
    assert cfg["poll_interval"] == 2.0
    assert cfg["ignore_patterns"] == [".git", ".env", ".cache"]


def test_get_config_defaults(monkeypatch: MonkeyPatch) -> None:
    """
    Test get_config returns defaults if env vars are missing (edge case).
    """
    monkeypatch.delenv("WATCHER_TIMEOUT", raising=False)
    monkeypatch.delenv("WATCHER_POLL_INTERVAL", raising=False)
    monkeypatch.delenv("WATCHER_IGNORE_PATTERNS", raising=False)
    config_mod = reload_config_module()
    cfg: config_mod_type.ConfigDict = config_mod.get_config()  # type: ignore[attr-defined]
    assert cfg["timeout"] == 2.0
    assert cfg["poll_interval"] == 1.0
    assert cfg["ignore_patterns"] == [".git", ".env"]


def test_get_config_invalid(monkeypatch: MonkeyPatch) -> None:
    """
    Test get_config handles invalid float values (failure case).
    """
    monkeypatch.setenv("WATCHER_TIMEOUT", "not_a_float")
    monkeypatch.setenv("WATCHER_POLL_INTERVAL", "not_a_float")
    config_mod = reload_config_module()
    with pytest.raises(ValueError):
        _ = config_mod.get_config()  # type: ignore[attr-defined]
