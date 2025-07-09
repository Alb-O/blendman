"""
Watcher-related CLI commands for blendman.
"""

import sys
import os
import typer  # type: ignore
from rich.console import Console  # type: ignore

# Ensure monorepo packages are importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../packages/rename_watcher/src")
    ),
)

from rename_watcher.config import get_config
from blendman.watcher_bridge import WatcherBridge
from blendman.db_interface import DBInterface
import time

watcher_app = typer.Typer()
console = Console()


@watcher_app.command()
def start(
    config_path: str = typer.Option(
        "watcher_config.toml", help="Path to watcher config TOML file."
    ),
):
    """
    Start the watcher with the given config and bridge events to the backend DB.
    """
    console.print(f"[bold green]Starting watcher with config:[/] {config_path}")
    os.environ["WATCHER_CONFIG_TOML"] = config_path
    try:
        config = get_config()
        console.print(f"[green]Loaded config:[/] {config}")
        db = DBInterface()
        bridge = WatcherBridge(db)
        bridge.start()
        console.print("[bold green]Watcher started. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("[yellow]Watcher stopped by user.")
    except Exception as e:
        console.print(f"[red]Error starting watcher:[/] {e}")


@watcher_app.command()
def stop():
    """
    Stop the watcher process (not implemented, placeholder).
    """
    console.print("[yellow]Stop command is not implemented in this version.")


@watcher_app.command()
def status():
    """
    Show watcher status (not implemented, placeholder).
    """
    console.print("[yellow]Status command is not implemented in this version.")
