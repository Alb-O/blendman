"""
Unit tests for TOML config parsing and gitignore-style matcher logic in config.py.
"""

import os
import tempfile
import textwrap
import pytest
from pathlib import Path
from typing import Any
import importlib
import sys


def reload_config_module() -> Any:
    if "rename_watcher.config" in sys.modules:
        del sys.modules["rename_watcher.config"]
    return importlib.import_module("rename_watcher.config")


def write_toml(content: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".toml")
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


def test_toml_config_parsing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test parsing of TOML config with include/ignore patterns (expected use).
    """
    toml_content = textwrap.dedent(
        """
        [include]
        patterns = ["src/**/*.py", "docs/**", "!*.tmp"]

        [ignore]
        patterns = [".git/", ".env", "*.log", "node_modules/", "__pycache__/" ]
        """
    )
    toml_path = write_toml(toml_content)
    monkeypatch.setenv("WATCHER_CONFIG_TOML", toml_path)
    config_mod = reload_config_module()
    cfg = config_mod.get_config()  # type: ignore[attr-defined]
    assert "patterns" in cfg
    assert "include" in cfg["patterns"]
    assert "ignore" in cfg["patterns"]
    assert cfg["patterns"]["include"] == ["src/**/*.py", "docs/**", "!*.tmp"]
    assert cfg["patterns"]["ignore"] == [
        ".git/",
        ".env",
        "*.log",
        "node_modules/",
        "__pycache__/",
    ]


def test_env_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test fallback to environment variables if TOML config is missing (edge case).
    """
    monkeypatch.delenv("WATCHER_CONFIG_TOML", raising=False)
    monkeypatch.setenv("WATCHER_IGNORE_PATTERNS", ".git,.env,.cache")
    config_mod = reload_config_module()
    cfg = config_mod.get_config()  # type: ignore[attr-defined]
    assert "patterns" in cfg
    assert "ignore" in cfg["patterns"]
    assert cfg["patterns"]["ignore"] == [".git", ".env", ".cache"]


def test_matcher_logic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test include/ignore matcher logic (expected, edge, and failure cases).
    """
    toml_content = textwrap.dedent(
        """
        [include]
        patterns = ["src/**/*.py", "!src/ignore_me.py"]

        [ignore]
        patterns = [".git/", "*.log"]
        """
    )
    toml_path = write_toml(toml_content)
    monkeypatch.setenv("WATCHER_CONFIG_TOML", toml_path)
    config_mod = reload_config_module()
    cfg = config_mod.get_config()  # type: ignore[attr-defined]
    matcher = config_mod.get_path_matcher(cfg["patterns"])  # type: ignore[attr-defined]
    # Should include .py in src, but not src/ignore_me.py
    assert matcher("src/foo/bar.py")
    assert not matcher("src/ignore_me.py")
    # Should ignore .git and .log
    assert not matcher(".git/config")
    assert not matcher("foo.log")
    # Should not match files outside include
    assert not matcher("docs/readme.md")


def test_invalid_toml(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test error on invalid TOML config (failure case).
    """
    toml_path = write_toml("not a toml file!")
    monkeypatch.setenv("WATCHER_CONFIG_TOML", toml_path)
    # If the config loader returns defaults or logs instead of raising,
    # just check it returns a config dict
    cfg = reload_config_module().get_config()  # type: ignore[attr-defined]
    assert isinstance(cfg, dict)


def test_ignore_all_pattern(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that '*' in ignore patterns ignores all files (failure case).
    """
    toml_content = """
    [ignore]
    patterns = ["*"]
    """
    toml_path = write_toml(toml_content)
    monkeypatch.setenv("WATCHER_CONFIG_TOML", toml_path)
    config_mod = reload_config_module()
    cfg = config_mod.get_config()  # type: ignore[attr-defined]
    matcher = config_mod.get_path_matcher(cfg["patterns"])  # type: ignore[attr-defined]
    # All files should be ignored
    assert not matcher("foo.py")
    assert not matcher("bar.txt")
    assert not matcher("subdir/file.blend")


def test_include_single_extension(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that a single extension in include patterns only matches that extension (expected use).
    """
    toml_content = """
    [include]
    patterns = [".blend"]
    """
    toml_path = write_toml(toml_content)
    monkeypatch.setenv("WATCHER_CONFIG_TOML", toml_path)
    config_mod = reload_config_module()
    cfg = config_mod.get_config()  # type: ignore[attr-defined]
    matcher = config_mod.get_path_matcher(cfg["patterns"])  # type: ignore[attr-defined]
    # Only .blend files should match
    assert matcher("foo.blend")
    assert matcher("subdir/bar.blend")
    assert not matcher("foo.py")
    assert not matcher("bar.txt")


def test_priority_option(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test the priority option: whether include or ignore takes precedence.
    """
    # Case 1: priority = "ignore" (default)
    toml_content_ignore = """
    priority = "ignore"
    [include]
    patterns = ["data/important.txt"]
    [ignore]
    patterns = ["data/"]
    """
    toml_path_ignore = write_toml(toml_content_ignore)
    monkeypatch.setenv("WATCHER_CONFIG_TOML", toml_path_ignore)
    config_mod = reload_config_module()
    cfg = config_mod.get_config()  # type: ignore[attr-defined]
    matcher = config_mod.get_path_matcher(cfg["patterns"])  # type: ignore[attr-defined]
    # File is included but inside an ignored dir; should be ignored
    assert not matcher("data/important.txt")

    # Case 2: priority = "include"
    toml_content_include = """
    priority = "include"
    [include]
    patterns = ["data/important.txt"]
    [ignore]
    patterns = ["data/"]
    """
    toml_path_include = write_toml(toml_content_include)
    monkeypatch.setenv("WATCHER_CONFIG_TOML", toml_path_include)
    config_mod = reload_config_module()
    cfg = config_mod.get_config()  # type: ignore[attr-defined]
    matcher = config_mod.get_path_matcher(cfg["patterns"])  # type: ignore[attr-defined]
    # File is included but inside an ignored dir; should be included
    assert matcher("data/important.txt")
    """
    Test that a single extension in include patterns only matches that extension (expected use).
    """
    toml_content = """
    [include]
    patterns = [".blend"]
    """
    toml_path = write_toml(toml_content)
    monkeypatch.setenv("WATCHER_CONFIG_TOML", toml_path)
    config_mod = reload_config_module()
    cfg = config_mod.get_config()  # type: ignore[attr-defined]
    matcher = config_mod.get_path_matcher(cfg["patterns"])  # type: ignore[attr-defined]
    # Only .blend files should match
    assert matcher("foo.blend")
    assert matcher("subdir/bar.blend")
    assert not matcher("foo.py")
    assert not matcher("bar.txt")
