"""Main entry point for the blendman application."""

from __future__ import annotations

import os
import shlex
import socket
import sys

from rich.console import Console
from rich.panel import Panel
from pyfiglet import Figlet
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

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
    """Run an interactive shell for executing CLI commands."""
    import click

    def is_pocketbase_running(host: str = "127.0.0.1", port: int = 8090) -> bool:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            return False

    def watcher_status(pidfile: str = "./.blendman_watcher.pid") -> str:
        if not os.path.exists(pidfile):
            return "off"
        try:
            with open(pidfile, "r", encoding="utf-8") as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            return "on"
        except Exception:  # pylint: disable=broad-exception-caught
            return "dead"

    def status_bar() -> str:
        pb = (
            "<ansigreen><b> PB: running </b></ansigreen>"
            if is_pocketbase_running()
            else "<ansired><b> PB: stopped </b></ansired>"
        )
        watch = watcher_status()
        watch_dirs = os.getenv("BLENDMAN_WATCH_PATH", os.getcwd())
        return f"{pb} watcher: {watch} | {watch_dirs}"

    style = Style.from_dict(
        {
            "prompt": "bold ansicyan",
            "bottom-toolbar": "fg:ansiwhite nobold",
        }
    )

    _print_logo()
    session = PromptSession(
        HTML("<prompt>blendman></prompt> "),
        bottom_toolbar=lambda: HTML(status_bar()),
        style=style,
    )

    aliases = {
        "watch": "watcher",
        "conf": "config",
        "pb": "pocketbase",
        "back": "backend",
    }
    command_groups = {"watcher", "config", "backend", "pocketbase"}
    while True:  # pragma: no cover - requires user interaction
        try:
            line = session.prompt()
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
        except click.UsageError:
            # Friendly error for unknown commands
            console.print(
                f"[yellow]Unknown command:[/] '{' '.join(args)}'\nType 'help' or exit."
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
