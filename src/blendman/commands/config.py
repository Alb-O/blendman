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
        "watcher_config.toml",
        help="Path to create the default watcher config TOML file.",
    ),
):
    """
    Create a default watcher_config.toml at the specified path.
    """
    default_config = """
[include]
patterns = ["*.blend", "*.txt"]

[ignore]
patterns = [".git", ".env", "__pycache__"]

priority = "ignore"
"""
    if os.path.exists(path):
        console.print(f"[yellow]Config file already exists at {path}.")
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(default_config)
        console.print(f"[green]Default watcher config created at {path}.")
    except Exception as e:
        console.print(f"[red]Failed to create config: {e}")
