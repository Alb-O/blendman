"""
Config management CLI commands for blendman.
"""

import os
import typer  # type: ignore
from rich.console import Console  # type: ignore


def create_default_config(path: str, app_console: Console | None = None) -> None:
    """Create a default TOML config if it doesn't already exist."""
    app_console = app_console or Console()
    default_config = """
priority = "include"

[include]
patterns = [".blend"]

[ignore]
patterns = ["*"]
"""
    if os.path.exists(path):
        app_console.print(f"[yellow]Config file already exists at {path}.")
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(default_config)
        app_console.print(f"[green]Default blendman config created at {path}.")
    except OSError as exc:
        app_console.print(f"[red]Failed to create config: {exc}")


config_app = typer.Typer()
console = Console()


@config_app.command()
def init(
    path: str = typer.Option(
        "blendman_config.toml",
        help="Path to create the default blendman config TOML file.",
    ),
):
    """Create a default blendman_config.toml at the specified path."""
    create_default_config(path, console)
