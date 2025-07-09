"""Main entry point for the blendman application."""

from rich.console import Console
from rich.panel import Panel
from pyfiglet import Figlet

from .cli import app

console = Console()


def main() -> None:
    """Run the Blendman Typer CLI with a friendly greeting and ASCII logo."""
    figlet = Figlet(font="larry3d")
    ascii_logo = figlet.renderText("BLENDMAN")
    console.print(
        Panel(
            ascii_logo,
            style="bold bluered`",
            width=75,
            subtitle="Welcome to Blendman CLI",
        )
    )
    app()


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()
