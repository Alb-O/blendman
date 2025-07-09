"""
Helper to start and stop the PocketBase server as a subprocess from Python.

Usage:
    from pocketbase_manager import PocketBaseManager
    pb = PocketBaseManager()
    pb.start()
    # ... interact with PocketBase at http://127.0.0.1:8090 ...
    pb.stop()
"""

# pylint: disable=consider-using-with
import subprocess
import os
import time
from typing import Optional
import typer
from rich.console import Console

console = Console()
app = typer.Typer()


class PocketBaseManager:
    """
    Manages the PocketBase server process.
    """

    def __init__(
        self,
        binary_path: Optional[str] = None,
        port: int = 8090,
        *,
        app_console: Console | None = None,
    ):
        """
        Args:
            binary_path (str, optional): Path to the PocketBase binary. Defaults to './pocketbase'.
            port (int): Port to run PocketBase on.
        """
        self.console = app_console or console
        self.binary_path = binary_path or os.path.join(
            os.path.dirname(__file__), "pocketbase"
        )
        self.port = port
        self.process: Optional[subprocess.Popen[bytes]] = None

    def start(self):
        """
        Starts the PocketBase server as a subprocess.
        """
        if self.process is not None:
            raise RuntimeError("PocketBase is already running.")
        self.process = subprocess.Popen(
            [self.binary_path, "serve", "--http", f"127.0.0.1:{self.port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # Wait a moment for the server to start
        time.sleep(2)
        self.console.print(
            f"[green]PocketBase started on http://127.0.0.1:{self.port}[/]"
        )

    def stop(self):
        """
        Stops the PocketBase server subprocess.
        """
        if self.process is None:
            self.console.print("[yellow]PocketBase is not running.")
            return
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
        self.console.print("[green]PocketBase stopped.")
        self.process = None


@app.command()
def start(port: int = typer.Option(8090, help="Port to run PocketBase on.")) -> None:
    """Start the PocketBase server and block until interrupted."""
    manager = PocketBaseManager(port=port, app_console=console)
    manager.start()
    console.print("Press Ctrl+C to stop PocketBase.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop()


@app.command()
def stop(port: int = typer.Option(8090, help="Port used for PocketBase.")) -> None:
    """Stop a running PocketBase server."""
    manager = PocketBaseManager(port=port, app_console=console)
    manager.stop()


def main() -> None:
    """Entry point for the Typer CLI."""
    app()


if __name__ == "__main__":
    main()
