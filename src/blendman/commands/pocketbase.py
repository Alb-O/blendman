"""
PocketBase-related CLI commands for blendman.
"""

import os
import webbrowser

import typer  # type: ignore
from rich.console import Console  # type: ignore

pocketbase_app = typer.Typer()
console = Console()


@pocketbase_app.command()
def login(email: str = typer.Option(None), password: str = typer.Option(None)):
    """Login to PocketBase and store token for the session."""
    from pocketbase.auth import AuthClient

    client = AuthClient()
    if not email:
        email = input("Email: ")
    if not password:
        import getpass

        password = getpass.getpass("Password: ")
    try:
        client.login(email, password)
        console.print("[green]Login successful")
    except Exception as exc:  # pylint: disable=broad-exception-caught
        console.print(f"[red]Login failed: {exc}")


@pocketbase_app.command()
def ui(
    open_root: bool = typer.Option(
        False, help="Open static root instead of dashboard UI"
    ),
):
    """
    Start PocketBase server and open dashboard UI or static root in browser.
    """
    console.print(
        "[green]Starting PocketBase server (not implemented, assumes running on :8090)..."
    )
    url = "http://127.0.0.1:8090/" if open_root else "http://127.0.0.1:8090/_/"
    if os.getenv("BLENDMAN_NO_BROWSER"):
        console.print(
            f"[yellow]BLENDMAN_NO_BROWSER set, not opening browser. URL: {url}"
        )
    else:
        webbrowser.open(url)
        console.print(f"[green]Opened {url}")


@pocketbase_app.command()
def superuser(email: str = typer.Argument(...), password: str = typer.Argument(...)):
    """
    Create the first superuser via CLI.
    """
    console.print(
        (
            f"[green]Creating superuser {email} "
            f"(not implemented, run './pocketbase superuser create {email} {password}')"
        )
    )


@pocketbase_app.command()
def migrate(action: str = typer.Argument(..., help="Action: run or list")):
    """
    Run or list JS migration scripts.
    """
    if action == "run":
        console.print(
            "[green]Running migrations (not implemented, run './pocketbase migrate up')"
        )
    elif action == "list":
        console.print(
            "[green]Listing migrations (not implemented, run './pocketbase migrate list')"
        )
    else:
        console.print("[red]Unknown action. Use 'run' or 'list'.")


@pocketbase_app.command(
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True}
)
def passthrough(ctx: typer.Context):
    """
    Pass through any PocketBase CLI command.
    """
    args = ctx.args
    console.print(
        f"[green]Passing through to PocketBase CLI: {' '.join(args)} (not implemented)"
    )
