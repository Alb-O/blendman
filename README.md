
# Blendman CLI

Blendman is a CLI tool for managing Blender-related workflows and PocketBase integration.

## Quickstart

### 1. Install dependencies

```sh
uv pip install -e .
```

### 2. Set up environment variables

Copy `.env.example` to `.env` and set:
- `POCKETBASE_URL`
- `POCKETBASE_ADMIN_EMAIL`
- `POCKETBASE_ADMIN_PASSWORD`
- `BLENDMAN_CONFIG` (optional)
These values are used on first launch to automatically create the PocketBase superuser
if it doesn't already exist.


### 3. Run the CLI

From the project root, set up your environment (for bash, zsh, etc.):

```sh
# Activate your virtual environment
. .venv/bin/activate
# Set the Python path for local packages
export PYTHONPATH=src:packages/rename_watcher/src:packages/pocketbase_backend/src
# See available commands
python -m blendman.cli --help
```

Replace `--help` with any command you want to run. For example:

- Start the watcher:
  ```sh
  python -m blendman.cli watcher start --config-path blendman_config.toml
  ```
  If `blendman_config.toml` doesn't exist, the CLI will create a default one for you.
  On first run the CLI will also start PocketBase automatically. If PocketBase hasn't
  been initialized yet you'll get instructions to create a superuser account.
- Check watcher status:
  ```sh
  python -m blendman.cli watcher status
  ```
- Query backend logs:
  ```sh
  python -m blendman.cli backend query logs
  ```
- Open PocketBase dashboard UI:
  ```sh
  python -m blendman.cli pocketbase ui
  ```
- Create a PocketBase superuser:
  ```sh
  python -m blendman.cli pocketbase superuser admin@example.com password
  ```

> **Tip:** If you use a different shell or platform, adapt the activation and environment variable commands as needed.

---

## Validation

To run all tests, lint, and type checks:

```sh
python dev.py
```

---

For advanced configuration and troubleshooting, see the documentation and `.env.example`.
