"""
Watcher-related CLI commands for blendman.
"""

import sys
import os
import typer  # type: ignore
from rich.console import Console  # type: ignore
import structlog  # type: ignore

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


def setup_logging():
    import logging

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )


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
    backend_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../packages/pocketbase_backend")
    )
    system = platform.system().lower()
    if system == "windows":
        bin_path = os.path.join(backend_dir, "pocketbase_bin.exe")
        cmd = [bin_path, "serve"]
        subprocess.Popen(
            cmd, cwd=backend_dir, creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        bin_path = os.path.join(backend_dir, "pocketbase_bin")
        cmd = [bin_path, "serve"]
        subprocess.Popen(cmd, cwd=backend_dir)
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
    watch_path: str = typer.Option(
        ".",
        help="Directory to watch for file changes (recursively watches all subdirectories, defaults to current directory).",
    ),
    pidfile: str = typer.Option(
        "./.blendman_watcher.pid", help="Path to PID file for watcher process."
    ),
):
    """
    Start the watcher with the given config and bridge events to the backend DB.
    Recursively watches all subdirectories of the specified directory.
    Writes a PID file for process management.
    """
    setup_logging()
    log = structlog.get_logger("blendman.cli")
    console.print(f"[bold green]Starting watcher with config:[/] {config_path}")
    os.environ["BLENDMAN_CONFIG_TOML"] = config_path
    try:
        start_pocketbase_if_needed(console)
        config = get_config()
        console.print(f"[green]Loaded config:[/] {config}")
        db = DBInterface()
        watch_abspath = os.path.abspath(watch_path)
        matcher = config.get("matcher")
        bridge = WatcherBridge(db, path=watch_abspath, matcher=matcher)
        # Write PID file
        with open(pidfile, "w") as f:
            f.write(str(os.getpid()))
        log.info(
            "Starting WatcherBridge",
            pid=os.getpid(),
            pidfile=pidfile,
            watch_path=watch_abspath,
        )
        bridge.start()
        console.print(
            f"[bold green]Watcher started. PID: {os.getpid()} (PID file: {pidfile}). Press Ctrl+C to stop."
        )
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Watcher stopped by user")
        console.print("[yellow]Watcher stopped by user.")
    except Exception as e:
        log.error("Error starting watcher", error=str(e))
        console.print(f"[red]Error starting watcher:[/] {e}")
    finally:
        # Remove PID file on exit
        if os.path.exists(pidfile):
            os.remove(pidfile)


@watcher_app.command()
def stop(
    pidfile: str = typer.Option(
        "./.blendman_watcher.pid", help="Path to PID file for watcher process."
    ),
):
    """
    Stop the watcher process if running (by PID file).
    """
    if not os.path.exists(pidfile):
        console.print(
            f"[yellow]No watcher PID file found at {pidfile}. Is the watcher running?"
        )
        return
    try:
        with open(pidfile, "r") as f:
            pid = int(f.read().strip())
        if platform.system().lower() == "windows":
            import ctypes

            PROCESS_TERMINATE = 1
            handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
            if not handle:
                raise OSError(f"Could not open process {pid}")
            result = ctypes.windll.kernel32.TerminateProcess(handle, -1)
            ctypes.windll.kernel32.CloseHandle(handle)
            if not result:
                raise OSError(f"Failed to terminate process {pid}")
        else:
            import signal

            os.kill(pid, signal.SIGTERM)
        console.print(f"[green]Stopped watcher process with PID {pid}.")
        os.remove(pidfile)
    except Exception as e:
        console.print(f"[red]Failed to stop watcher: {e}")


@watcher_app.command()
def status(
    pidfile: str = typer.Option(
        "./.blendman_watcher.pid", help="Path to PID file for watcher process."
    ),
):
    """
    Show watcher status (running or not, by PID file).
    """
    if not os.path.exists(pidfile):
        console.print(f"[yellow]Watcher is not running (no PID file at {pidfile}).")
        return
    try:
        with open(pidfile, "r") as f:
            pid = int(f.read().strip())
        # Check if process is alive
        if platform.system().lower() == "windows":
            import ctypes

            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_LIMITED_INFORMATION, False, pid
            )
            if handle:
                ctypes.windll.kernel32.CloseHandle(handle)
                alive = True
            else:
                alive = False
        else:
            try:
                os.kill(pid, 0)
                alive = True
            except OSError:
                alive = False
        if alive:
            console.print(f"[green]Watcher is running (PID {pid}).")
        else:
            console.print(
                f"[yellow]Watcher PID file exists but process {pid} is not running."
            )
    except Exception as e:
        console.print(f"[red]Error checking watcher status: {e}")
