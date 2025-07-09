"""
Config management CLI commands for blendman.
"""

import os
import typer  # type: ignore
from rich.console import Console  # type: ignore

config_app = typer.Typer()
console = Console()


@config_app.command()
def init(
    path: str = typer.Option(
        "blendman_config.toml",
        help="Path to create the default blendman config TOML file.",
    ),
):
    """
    Create a default blendman_config.toml at the specified path.
    """
    default_config = """
[include]
patterns = [".blend"]

[ignore]
patterns = ["*"]

priority = "include"
"""
    if os.path.exists(path):
        console.print(f"[yellow]Config file already exists at {path}.")
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(default_config)
        console.print(f"[green]Default blendman config created at {path}.")
    except OSError as exc:
        console.print(f"[red]Failed to create config: {exc}")
