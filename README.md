# Blendman Workspace (uv)

This project uses [uv workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/) for robust, idiomatic Python monorepo management.

## Structure

- `pyproject.toml` (root): Declares the workspace and manages shared dependencies and scripts.
- `packages/pocketbase/`: Contains the PocketBase binary manager package.
- `src/blendman/`: Main application code and CLI entry points.

## Workflow

### Install all dependencies (including dev tools)

```sh
uv pip install -e .
```

### Run the PocketBase manager CLI

```sh
uv run --package pocketbase pocketbase-manager start --port 8090
```


### Lint and type-check the entire workspace

```sh
uv run ruff check .
./mypy_recursive.sh
```

### Add a new package

- Create a new directory under `packages/` with its own `pyproject.toml` and `src/`.
- Add it to the `members` list in the root `pyproject.toml` if not using a glob.

## Best Practices

- Use `[tool.uv.sources]` for local package dependencies.
- Keep dev tools (ruff, mypy, pytest, etc.) in the root dependencies for workspace-wide use.
- Use `uv run` and `uv pip` from the workspace root for all operations.

See [uv workspace docs](https://docs.astral.sh/uv/concepts/projects/workspaces/) for more details.
