# NOTEPAD for 005_cli_interface

## Purpose
Track planning, brainstorming, and task progress for the CLI interface feature.


## [2025-07-09] Implementation Plan

### CLI Structure
- Use Typer for the main CLI app: `src/blendman/cli.py`.
- Organize subcommands in `src/blendman/commands/`:
	- `watcher.py`: watcher start/stop/status
	- `config.py`: config init
	- `backend.py`: backend query/manage
	- `pocketbase.py`: UI, superuser, migrations, passthrough

### Key Steps
1. Scaffold `src/blendman/cli.py` as Typer app.
2. Create `src/blendman/commands/` and add modules for each command group.
3. Implement watcher commands (start/stop/status) with config file support.
4. Implement config init command (create default TOML config).
5. Implement backend query/manage commands (list files/logs, start/stop PB server).
6. Implement PocketBase commands (UI, superuser, migrations, passthrough).
7. Use `rich` for output formatting.
8. Ensure config/env loading via python-dotenv and TOML.
9. Add error handling and logging for all commands.
10. Write unit tests for all CLI commands in `tests/blendman/test_cli.py`.
11. Update `.env.example` and `README.md` for CLI usage.
12. Run all validation gates: tests, lint, type checks, manual CLI help.

### TODOs
- [x] Scaffold CLI app and command modules
- [x] Implement watcher commands
- [x] Implement config management
- [x] Implement backend commands
- [x] Implement PocketBase commands
- [x] Add error handling/logging
- [x] Write unit tests
- [x] Update docs and env example
- [x] Validate and iterate until all gates pass

## [2025-07-09] Completion
- All CLI commands implemented and tested.
- All validation gates (tests, lint, type checks) pass.
- Documentation and .env.example updated.
- Feature ready for review/merge.
