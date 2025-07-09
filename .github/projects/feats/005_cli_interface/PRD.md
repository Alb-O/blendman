# 005_cli_interface: Product Requirements Document (PRD)

## Purpose
Design and implement a comprehensive, idiomatic CLI for the blendman program, bridging the backend (PocketBase) and watcher (rename_watcher) functionality. The CLI must support recursive directory watching, TOML config management, and provide a robust, user-friendly interface with multiple subcommands and readable output. All implementation must be self-validating and follow best practices for Python CLI tools.

## Why
- **Business Value:** Enables users to control and monitor file/directory state and history from the command line, integrating backend and watcher features.
- **Integration:** Bridges `pocketbase_backend` and `rename_watcher` via a unified CLI, supporting config management and event logging.
- **User Impact:** Simplifies setup, monitoring, and troubleshooting for end users and developers.

## What (Explicit Agent Behaviors)
- CLI must expose subcommands for:
  - Starting/stopping the watcher (with config file support)
  - Initializing a config file at the root
  - Querying backend state (files, logs, etc.)
  - Managing PocketBase server (start/stop/status)
  - **PocketBase UI/dashboard management:**
    - Start the PocketBase server and open the dashboard UI in the browser ([http://127.0.0.1:8090/_/](http://127.0.0.1:8090/_/))
    - Option to open the static content root ([http://127.0.0.1:8090/](http://127.0.0.1:8090/))
  - **Superuser management:**
    - Create the first superuser via CLI (`./pocketbase superuser create EMAIL PASS`)
  - **Migrations:**
    - Run/list JS migration scripts in `pb_migrations` ([docs](https://pocketbase.io/docs/js-migrations))
  - **Help and passthrough commands:**
    - Expose `cli pocketbase --help` and `cli pocketbase [command] --help` for full PocketBase command discovery
- Use idiomatic CLI library (Typer recommended)
- Auto-detect config files and environment variables
- Provide clear, readable output (use `rich` if needed)
- All commands must be testable and covered by unit tests
- All errors must be logged and handled gracefully

### Success Criteria (Validation Gates)
- [ ] All CLI commands have unit tests (happy, edge, and failure cases)
- [ ] `./dev.sh` passes (lint, type-check, test)
- [ ] All errors are logged and handled
- [ ] CLI help and subcommands are discoverable and documented

## All Needed Context (Critical Context Awareness)

### Documentation & References
```yaml
- url: https://typer.tiangolo.com/
  why: Typer CLI library documentation, subcommands, error handling, best practices
- url: https://typer.tiangolo.com/tutorial/subcommands/
  why: Subcommand patterns, grouping, and help
- url: https://typer.tiangolo.com/tutorial/testing/
  why: Testing Typer CLIs
- url: https://rich.readthedocs.io/en/stable/
  why: For pretty CLI output
- url: https://pocketbase.io/docs/
  why: PocketBase official documentation, CLI commands, UI/dashboard, superuser, migrations
- url: https://pocketbase.io/docs/js-migrations
  why: JS migration scripts for PocketBase
- file: src/blendman/main.py
  why: Current CLI entry point (to be replaced/extended)
- file: src/blendman/pocketbase_manager_cli.py
  why: Example of CLI entry for backend management
- file: packages/rename_watcher/src/rename_watcher/config.py
  why: Config file loading and TOML parsing
- file: packages/rename_watcher/src/rename_watcher/api.py
  why: Watcher API for event subscription
- file: packages/pocketbase_backend/src/pocketbase/api.py
  why: Backend API for DB operations
- file: src/blendman/db_interface.py
  why: Interface for DB operations
- file: src/blendman/watcher_bridge.py
  why: Bridge between watcher and backend
- file: .github/projects/templates/PRD.md
  why: PRD structure and validation requirements
```

### Current Codebase tree (run `tree` in the root of the project)
```bash
# See workspace structure above
```

### Desired Codebase tree with files to be added and responsibility of file
```bash
src/blendman/cli.py         # Main Typer app, all subcommands
src/blendman/commands/      # (optional) Subcommand modules for organization
  watcher.py                # Watcher-related CLI commands
  backend.py                # Backend-related CLI commands
  config.py                 # Config management commands
  pocketbase.py             # PocketBase-specific commands (UI, superuser, migrations, passthrough)
tests/blendman/test_cli.py  # Unit tests for CLI
.env.example                # Example env file for CLI/config
README.md                   # Updated with CLI usage and setup
```

### Known Gotchas of our codebase & Library Quirks
```python
# Typer requires all CLI entry points to be functions, not classes
# Use @app.command() for each subcommand
# Use python-dotenv and load_env() for env vars
# All config must be loaded via TOML or env, never hardcoded
# If any validation gate fails, debug, fix, and re-run until it passes. Document root causes and solutions.
# PocketBase server must be running for backend commands
# Watcher must handle cross-platform file events
# PocketBase UI is at http://127.0.0.1:8090/_/ and static root at http://127.0.0.1:8090/
# Superuser creation: ./pocketbase superuser create EMAIL PASS
# Migrations: ./pocketbase migrate ... (see docs)
# All PocketBase commands: ./pocketbase --help
```

## Implementation Blueprint
- Use Typer to define a main CLI app (`src/blendman/cli.py`)
- Add subcommands for:
  - `watcher start/stop/status` (with config file support)
  - `config init` (create default TOML config)
  - `backend query` (list files/logs)
  - `backend manage` (start/stop PocketBase)
  - `pocketbase ui` (start server and open dashboard UI in browser)
  - `pocketbase superuser` (create/manage superusers)
  - `pocketbase migrate` (run/list migrations)
  - `pocketbase passthrough` (expose all PocketBase CLI commands)
- Use `rich` for pretty output (optional, but recommended)
- Load config using `python-dotenv` and TOML parser
- Bridge watcher and backend via `WatcherBridge` and `DBInterface`
- Add unit tests for all CLI commands in `tests/blendman/test_cli.py`
- Update `.env.example` and `README.md` for CLI usage

### Pseudocode Example
```python
import typer
from rich.console import Console
from .watcher_bridge import WatcherBridge
from .db_interface import DBInterface

app = typer.Typer()
console = Console()

@app.command()
def watcher_start(config: str = "watcher_config.toml"):
    # Load config, start watcher, bridge events to DB
    ...

@app.command()
def config_init():
    # Create default TOML config at root
    ...

@app.command()
def backend_query(query_type: str):
    # Query backend for files/logs
    ...

@app.command()
def backend_manage(command: str):
    # Start/stop PocketBase server
    ...

@app.command()
def pocketbase_ui():
    # Start PocketBase server and open dashboard UI in browser
    ...

@app.command()
def pocketbase_superuser(email: str, password: str):
    # Create superuser
    ...

@app.command()
def pocketbase_migrate(action: str):
    # Run/list migrations
    ...

@app.command()
def pocketbase_passthrough(args: list[str]):
    # Pass through any PocketBase CLI command
    ...

if __name__ == "__main__":
    app()
```

## Validation Loop (Agent Self-Validation & Iteration)
### Level 1: Syntax & Style
```bash
./dev.sh
# Expected: No errors or warnings. If errors/warnings, analyze, fix, and re-run until passing.
```
### Level 2: Unit Tests
- All CLI commands must have unit tests in `tests/blendman/test_cli.py`
- Use Typer's test client for CLI testing (see https://typer.tiangolo.com/tutorial/testing/)
```bash
uv run pytest
```

## Final validation Checklist
- [ ] All tests pass
- [ ] No linting errors (`ruff check .`)
- [ ] No type errors (`mypy .`)
- [ ] Manual test successful: `python -m blendman.cli --help`
- [ ] Error cases handled gracefully and are documented
- [ ] Logs are informative but not verbose
- [ ] Documentation updated if needed
- [ ] All validation gates are self-checked and iterated until passing

## Score: 10/10
- All context and validation gates included. One-pass implementation is highly likely if all steps are followed.
