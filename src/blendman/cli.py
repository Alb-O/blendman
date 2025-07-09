"""
Main Typer CLI app for blendman.
"""

import typer
from rich.console import Console
from blendman.commands.watcher import watcher_app
from blendman.commands.config import config_app
from blendman.commands.backend import backend_app
from blendman.commands.pocketbase import pocketbase_app

app = typer.Typer()
console = Console()

# Register sub-apps as command groups
app.add_typer(watcher_app, name="watcher", help="Watcher-related commands")
app.add_typer(config_app, name="config", help="Config management commands")
app.add_typer(backend_app, name="backend", help="Backend management commands")
app.add_typer(
    pocketbase_app, name="pocketbase", help="PocketBase server and migrations"
)

if __name__ == "__main__":
    app()
