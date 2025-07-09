"""
Backend-related CLI commands for blendman.
"""

import typer  # type: ignore
from rich.console import Console  # type: ignore
from blendman.db_interface import DBInterface

backend_app = typer.Typer()
console = Console()


@backend_app.command()
def query(
    type: str = typer.Argument(..., help="Type of query: files or logs"),
    file_id: str = typer.Option(None, help="File ID for logs or state queries"),
):
    """
    Query backend for files or logs.
    """
    db = DBInterface()
    if type == "files":
        if file_id:
            result = db.get_file_state(file_id)
            console.print(result)
        else:
            console.print("[yellow]Listing all files is not implemented.")
    elif type == "logs":
        if file_id:
            logs = db.get_logs_for_file(file_id)
            console.print(logs)
        else:
            logs = db.get_global_log()
            console.print(logs)
    else:
        console.print("[red]Unknown query type. Use 'files' or 'logs'.")


@backend_app.command()
def manage(command: str = typer.Argument(..., help="Command: start or stop")):
    """
    Start or stop the PocketBase server (placeholder).
    """
    if command == "start":
        console.print("[green]Starting PocketBase server (not implemented).")
    elif command == "stop":
        console.print("[yellow]Stopping PocketBase server (not implemented).")
    else:
        console.print("[red]Unknown command. Use 'start' or 'stop'.")
