"""
Watcher-related CLI commands for blendman.
"""

import sys
import os
import typer  # type: ignore
from rich.console import Console  # type: ignore
import subprocess
import platform
import socket

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

def is_pocketbase_running(host: str = "127.0.0.1", port: int = 8090) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False

def start_pocketbase_if_needed(console):
    if is_pocketbase_running():
        console.print("[green]PocketBase server is already running.")
        return
    console.print("[yellow]PocketBase server not detected. Attempting to start it...")
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../packages/pocketbase_backend"))
    system = platform.system().lower()
    if system == "windows":
        bin_path = os.path.join(backend_dir, "pocketbase_bin.exe")
        cmd = [bin_path, "serve"]
        proc = subprocess.Popen(cmd, cwd=backend_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        bin_path = os.path.join(backend_dir, "pocketbase_bin")
        cmd = [bin_path, "serve"]
        proc = subprocess.Popen(cmd, cwd=backend_dir)
    # Wait for server to be available
    for _ in range(20):
        if is_pocketbase_running():
            console.print("[green]PocketBase server started.")
            return
        time.sleep(0.5)
    raise RuntimeError("PocketBase server did not start within 10 seconds.")

@watcher_app.command()
def start(
    config_path: str = typer.Option(
        "blendman_config.toml", help="Path to blendman config TOML file."
    ),
):
    """
    Start the watcher with the given config and bridge events to the backend DB.
    """
    console.print(f"[bold green]Starting watcher with config:[/] {config_path}")
    os.environ["BLENDMAN_CONFIG_TOML"] = config_path
    try:
        start_pocketbase_if_needed(console)
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
