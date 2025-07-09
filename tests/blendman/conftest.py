"""
Pytest fixture to ensure PocketBase has required collections for integration tests.
"""

import pytest  # type: ignore
import requests
import os

POCKETBASE_URL = os.environ.get("POCKETBASE_URL", "http://127.0.0.1:8090")
ADMIN_EMAIL = os.environ.get("POCKETBASE_ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.environ.get("POCKETBASE_ADMIN_PASSWORD", "changeme")


@pytest.fixture(scope="session", autouse=True)
def ensure_pocketbase_collections():
    """
    Ensure PocketBase has 'files' and 'rename_logs' collections for integration tests.
    Skips tests if PocketBase is not running or cannot be seeded.
    """
    try:
        # Login as admin
        resp = requests.post(
            f"{POCKETBASE_URL}/api/collections/_superusers/auth-with-password",
            json={
                "identity": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD,
            },
            timeout=5,
        )
        resp.raise_for_status()
        token = resp.json().get("token")
        headers = {"Authorization": token}
        # Create 'files' collection if missing
        files_resp = requests.get(
            f"{POCKETBASE_URL}/api/collections/files", headers=headers, timeout=5
        )
        if files_resp.status_code == 404:
            requests.post(
                f"{POCKETBASE_URL}/api/collections",
                headers=headers,
                json={
                    "name": "files",
                    "type": "base",
                    "schema": [
                        {"name": "name", "type": "text", "required": True},
                        {"name": "path", "type": "text", "required": True},
                        {"name": "parent_id", "type": "text"},
                        {"name": "type", "type": "text", "required": True},
                    ],
                },
                timeout=5,
            )
        # Create 'rename_logs' collection if missing
        logs_resp = requests.get(
            f"{POCKETBASE_URL}/api/collections/rename_logs", headers=headers, timeout=5
        )
        if logs_resp.status_code == 404:
            requests.post(
                f"{POCKETBASE_URL}/api/collections",
                headers=headers,
                json={
                    "name": "rename_logs",
                    "type": "base",
                    "schema": [
                        {"name": "file_id", "type": "text", "required": True},
                        {"name": "old_path", "type": "text"},
                        {"name": "new_path", "type": "text", "required": True},
                        {"name": "event_type", "type": "text", "required": True},
                    ],
                },
                timeout=5,
            )
    except Exception as e:
        pytest.skip(f"PocketBase not available or could not seed collections: {e}")
