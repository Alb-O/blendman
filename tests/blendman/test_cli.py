"""
Unit tests for the blendman CLI using Typer's test client.
"""

import sys
import os
from typer.testing import CliRunner  # type: ignore

# Ensure monorepo packages are importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src"))
)

from blendman.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "watcher" in result.output
    assert "config" in result.output
    assert "backend" in result.output
    assert "pocketbase" in result.output


def test_config_init(tmp_path):
    config_path = tmp_path / "test_watcher_config.toml"
    result = runner.invoke(app, ["config", "init", "--path", str(config_path)])
    assert result.exit_code == 0
    assert config_path.exists()
    with open(config_path) as f:
        content = f.read()
        assert "[include]" in content
        assert "[ignore]" in content


def test_watcher_status():
    result = runner.invoke(app, ["watcher", "status"])
    assert result.exit_code == 0
    assert "Status command is not implemented" in result.output


def test_backend_manage():
    result = runner.invoke(app, ["backend", "manage", "start"])
    assert result.exit_code == 0
    assert "Starting PocketBase server" in result.output
    result = runner.invoke(app, ["backend", "manage", "stop"])
    assert result.exit_code == 0
    assert "Stopping PocketBase server" in result.output


def test_pocketbase_ui(monkeypatch):
    monkeypatch.setenv("BLENDMAN_NO_BROWSER", "1")
    result = runner.invoke(app, ["pocketbase", "ui", "--open-root"])
    assert result.exit_code == 0
    assert "BLENDMAN_NO_BROWSER set, not opening browser" in result.output


def test_pocketbase_superuser():
    result = runner.invoke(
        app, ["pocketbase", "superuser", "test@example.com", "password"]
    )
    assert result.exit_code == 0
    assert "Creating superuser" in result.output


def test_pocketbase_migrate():
    result = runner.invoke(app, ["pocketbase", "migrate", "run"])
    assert result.exit_code == 0
    assert "Running migrations" in result.output
    result = runner.invoke(app, ["pocketbase", "migrate", "list"])
    assert result.exit_code == 0
    assert "Listing migrations" in result.output


def test_pocketbase_passthrough():
    result = runner.invoke(app, ["pocketbase", "passthrough", "echo"])
    assert result.exit_code == 0
    assert (
        "Passing through to PocketBase CLI" in result.output
        or "not implemented" in result.output
    )
