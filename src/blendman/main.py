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
            style="bold blue",
            width=75,
            subtitle="Welcome to Blendman CLI",
        )
    )


def interactive_shell() -> None:
    """Run an interactive shell for executing CLI commands."""
    import click

    _print_logo()
    # Aliases for common typos/shortcuts
    aliases = {
        "watch": "watcher",
        "conf": "config",
        "pb": "pocketbase",
        "back": "backend",
    }
    # Get available command groups for help fallback
    command_groups = {"watcher", "config", "backend", "pocketbase"}
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
        if line.strip() == "help":
            # Print main CLI help
            app(["--help"], standalone_mode=False)
            continue
        args = shlex.split(line)
        # Alias fallback: replace first arg if it's a known alias
        if args and args[0] in aliases:
            args[0] = aliases[args[0]]
        # If only a group is entered, show its help
        if len(args) == 1 and args[0] in command_groups:
            app([args[0], "--help"], standalone_mode=False)
            continue
        try:
            app(args, standalone_mode=False)
        except click.UsageError as exc:
            # Friendly error for unknown commands
            console.print(
                f"[yellow]Unknown command:[/] '{' '.join(args)}'\nType 'help' or 'exit'."
            )
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
