"""Main entry point for the blendman application."""

from __future__ import annotations

import shlex
import sys

from rich.console import Console
from rich.panel import Panel
from pyfiglet import Figlet

from .cli import app

console = Console()


def _print_logo() -> None:
    """Print the Blendman ASCII logo once when entering the shell."""
    figlet = Figlet(font="larry3d")
    ascii_logo = figlet.renderText("BLENDMAN")
    console.print(
        Panel(
            ascii_logo,
            style="bold bluered",
            width=75,
            subtitle="Welcome to Blendman CLI",
        )
    )


def interactive_shell() -> None:
    """Run an interactive shell for executing CLI commands."""
    _print_logo()
    while True:  # pragma: no cover - requires user interaction
        try:
            line = input("blendman> ")
        except (EOFError, KeyboardInterrupt):
            console.print()
            break
        if not line.strip():
            continue
        if line.strip() in {"exit", "quit"}:
            break
        args = shlex.split(line)
        try:
            app(args, standalone_mode=False)
        except SystemExit as exc:  # pragma: no cover - handled gracefully
            if exc.code != 0:
                console.print(f"[red]Command failed with code {exc.code}")


def main() -> None:
    """Start interactive shell or run a one-off command."""
    if len(sys.argv) > 1:
        app(sys.argv[1:])
    else:
        interactive_shell()


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()
