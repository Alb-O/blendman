pb.start()
# ... interact with PocketBase at http://127.0.0.1:8090 ...
pb.stop()

# PocketBase Python API Client

This package provides a modular Python API client for [PocketBase](https://pocketbase.io/) using its REST API.

## Setup

1. Copy `.env.example` to `.env` and fill in your PocketBase server details:

    `cp .env.example .env`

2. Install dependencies (in your uv workspace):

    `uv sync`

3. Run validation gates:

    `./dev.sh`

## Environment Variables

See `.env.example` for required variables:

    POCKETBASE_URL=http://127.0.0.1:8090
    POCKETBASE_ADMIN_EMAIL=admin@example.com
    POCKETBASE_ADMIN_PASSWORD=changeme

## Usage Example

```python
from pocketbase.api import PocketBaseAPI

api = PocketBaseAPI()

# Auth
api.auth.login(email="admin@example.com", password="changeme")

# CRUD
record = api.collections.create("users", {"username": "alice"})
user = api.collections.get("users", record["id"])

# Relations
api.relations.link("users", user["id"], "friends", "other_user_id")

# Files
# api.files.upload(...)

# Logout
api.auth.logout()
```

## Notes
- All API errors are wrapped in custom exceptions (see `exceptions.py`).
- All HTTP requests in tests are mocked; no real PocketBase server is required for unit tests.
- For more information, see the [PocketBase documentation](https://pocketbase.io/docs/).
