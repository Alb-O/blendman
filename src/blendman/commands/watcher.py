"""
Watcher-related CLI commands for blendman.
"""

# pylint: disable=consider-using-with

import os
import logging
import platform
import signal
import socket
import subprocess
import time

import structlog  # type: ignore
import typer  # type: ignore
from rich.console import Console  # type: ignore
from rich.logging import RichHandler

from rename_watcher.config import get_config
from blendman.watcher_bridge import WatcherBridge
from blendman.db_interface import DBInterface
from blendman.commands.config import create_default_config


def setup_logging() -> None:
    """Configure rich logging for the CLI."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


watcher_app = typer.Typer()
console = Console()


def is_pocketbase_running(host: str = "127.0.0.1", port: int = 8090) -> bool:
    """Check if the PocketBase server is reachable."""
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


def start_pocketbase_if_needed(app_console: Console) -> None:
    """Start PocketBase if not running and guide the user through first-time setup."""
    if is_pocketbase_running():
        app_console.print("[green]PocketBase server is already running.")
        return

    backend_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../packages/pocketbase_backend")
    )
    pb_data_dir = os.path.join(backend_dir, "pb_data")
    first_run = not os.path.exists(pb_data_dir)

    system = platform.system().lower()
    if system == "windows":
        bin_path = os.path.join(backend_dir, "pocketbase_bin.exe")
        serve_cmd = [bin_path, "serve"]
        creationflags = subprocess.CREATE_NEW_CONSOLE
    else:
        bin_path = os.path.join(backend_dir, "pocketbase_bin")
        serve_cmd = [bin_path, "serve"]
        creationflags = 0

    if not os.path.exists(bin_path):
        app_console.print(
            "[red]PocketBase binary not found. Run 'python packages/pocketbase_backend/download_pocketbase.py' to download it."
        )
        raise FileNotFoundError("PocketBase binary missing")

    app_console.print(
        "[yellow]PocketBase server not detected. Attempting to start it..."
    )
    subprocess.Popen(serve_cmd, cwd=backend_dir, creationflags=creationflags)  # pylint: disable=consider-using-with

    # Wait for server to become reachable
    for _ in range(20):
        if is_pocketbase_running():
            app_console.print("[green]PocketBase server started.")
            break
        time.sleep(0.5)
    else:
        raise RuntimeError("PocketBase server did not start within 10 seconds.")

    if first_run:
        admin_email = os.environ.get("POCKETBASE_ADMIN_EMAIL")
        admin_pass = os.environ.get("POCKETBASE_ADMIN_PASSWORD")
        if admin_email and admin_pass:
            app_console.print(
                "[yellow]Initializing PocketBase with provided admin credentials..."
            )
            try:
                subprocess.run(
                    [bin_path, "superuser", "upsert", admin_email, admin_pass],
                    cwd=backend_dir,
                    check=True,
                    capture_output=True,
                )
                app_console.print("[green]Superuser account created or updated.")
            except subprocess.CalledProcessError as exc:
                app_console.print(
                    f"[red]Failed to create superuser automatically: {exc}."
                )
                app_console.print(
                    f"Run '{bin_path} superuser upsert <EMAIL> <PASSWORD>' manually or visit http://127.0.0.1:8090/_/ in your browser to finish setup."
                )
        else:
            app_console.print(
                "[yellow]PocketBase appears uninitialized. Visit http://127.0.0.1:8090/_/ in your browser to create a superuser,"
            )
            app_console.print(
                f"or run '{bin_path} superuser upsert <EMAIL> <PASSWORD>' from the command line."
            )


@watcher_app.command()
def start(
    config_path: str = typer.Option(
        "blendman_config.toml", help="Path to blendman config TOML file."
    ),
    watch_path: str = typer.Option(
        ".",
        help=(
            "Directory to watch for file changes (recursively watches all "
            "subdirectories, defaults to current directory)."
        ),
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
    if not os.path.exists(config_path):
        console.print(
            f"[yellow]No config found at {config_path}. Creating default one."
        )
        create_default_config(config_path, console)
    try:
        start_pocketbase_if_needed(console)
        config = get_config()
        console.print(f"[green]Loaded config:[/] {config}")
        if not os.environ.get("POCKETBASE_ADMIN_EMAIL") or not os.environ.get(
            "POCKETBASE_ADMIN_PASSWORD"
        ):
            console.print(
                "[red]PocketBase admin credentials missing. Set POCKETBASE_ADMIN_EMAIL and POCKETBASE_ADMIN_PASSWORD in the environment or a .env file."
            )
            console.print("Example: cp .env.example .env && edit the values.")
            return
        db = DBInterface()
        watch_abspath = os.path.abspath(watch_path)
        matcher = config.get("matcher")
        bridge = WatcherBridge(db, path=watch_abspath, matcher=matcher)
        # Write PID file
        with open(pidfile, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
        log.info(
            "Starting WatcherBridge",
            pid=os.getpid(),
            pidfile=pidfile,
            watch_path=watch_abspath,
        )
        bridge.start()
        console.print(
            (
                f"[bold green]Watcher started. PID: {os.getpid()} "
                f"(PID file: {pidfile}). Press Ctrl+C to stop."
            )
        )
        while True:
            time.sleep(1)
    except ValueError as exc:
        log.error("Configuration error", error=str(exc))
        console.print(f"[red]{exc}")
    except KeyboardInterrupt:
        log.info("Watcher stopped by user")
        console.print("[yellow]Watcher stopped by user.")
    except Exception as exc:  # pylint: disable=broad-exception-caught
        log.error("Error starting watcher", error=str(exc))
        console.print(f"[red]Error starting watcher:[/] {exc}")
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
        with open(pidfile, "r", encoding="utf-8") as f:
            pid = int(f.read().strip())
        if platform.system().lower() == "windows":
            import ctypes  # pylint: disable=import-outside-toplevel

            process_terminate = 1
            handle = ctypes.windll.kernel32.OpenProcess(process_terminate, False, pid)
            if not handle:
                raise OSError(f"Could not open process {pid}")
            result = ctypes.windll.kernel32.TerminateProcess(handle, -1)
            ctypes.windll.kernel32.CloseHandle(handle)
            if not result:
                raise OSError(f"Failed to terminate process {pid}")
        else:
            os.kill(pid, signal.SIGTERM)
        console.print(f"[green]Stopped watcher process with PID {pid}.")
        os.remove(pidfile)
    except OSError as exc:
        console.print(f"[red]Failed to stop watcher: {exc}")


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
        with open(pidfile, "r", encoding="utf-8") as f:
            pid = int(f.read().strip())
        # Check if process is alive
        if platform.system().lower() == "windows":
            import ctypes  # pylint: disable=import-outside-toplevel

            process_query_limited_information = 0x1000
            handle = ctypes.windll.kernel32.OpenProcess(
                process_query_limited_information, False, pid
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
    except (OSError, ValueError) as exc:
        console.print(f"[red]Error checking watcher status: {exc}")
