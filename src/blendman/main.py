"""Main entry point for the blendman application."""

from __future__ import annotations

import os
import sys

from rich.console import Console
from rich.panel import Panel
from pyfiglet import Figlet
from .prompt_ui import run_shell

from .cli import app

console = Console()


def _print_logo() -> None:
    """Print the Blendman ASCII logo once when entering the shell."""
    figlet = Figlet(font="larry3d")
    ascii_logo = figlet.renderText("BLENDMAN")
    console.print(
        Panel(
            ascii_logo,
            style="bold blue",
            width=75,
            subtitle="Welcome to Blendman CLI. Type <help> for commands.",
        )
    )


def interactive_shell() -> None:
    """Run an interactive shell using the prompt_toolkit UI."""
    os.environ["BLENDMAN_INTERACTIVE"] = "1"
    _print_logo()
    run_shell()


def main() -> None:
    """Start interactive shell or run a one-off command."""
    if len(sys.argv) > 1:
        app(sys.argv[1:])
    else:
        interactive_shell()


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()
