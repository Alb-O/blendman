import os
import time
import pytest
from blendman.db_interface import DBInterface
from blendman.watcher_bridge import WatcherBridge


@pytest.mark.integration
def test_end_to_end_file_create_and_log(monkeypatch):
    try:
        import requests

        requests.get("http://127.0.0.1:8090/api/collections")
    except Exception:
        pytest.skip("PocketBase server not running; skipping integration test.")
    """
    End-to-end test: Simulate watcher event, persist to PocketBase, and validate DB entries.
    - Starts PocketBase (assumes running or fixture)
    - Simulates a file creation event
    - Validates FileDir and RenameLog entries in PocketBase
    """
    # Setup: ensure env vars for PocketBase admin
    os.environ["POCKETBASE_URL"] = "http://127.0.0.1:8090"
    os.environ["POCKETBASE_ADMIN_EMAIL"] = "admin@example.com"
    os.environ["POCKETBASE_ADMIN_PASSWORD"] = "changeme"

    db = DBInterface()
    bridge = WatcherBridge(db)

    # Simulate watcher event (file created)
    event = {
        "name": "testfile.txt",
        "new_path": "/tmp/testfile.txt",
        "type": "file",
        "event_type": "create",
    }
    bridge.handle_event(event)

    # Wait for DB to persist (if async)
    time.sleep(0.5)

    # Use superuser token if available
    import requests

    superuser_token = os.environ.get("POCKETBASE_SUPERUSER_TOKEN")
    headers = {}
    if superuser_token:
        headers = {"Authorization": superuser_token}

    # Query PocketBase for file entry
    url = "http://127.0.0.1:8090/api/collections/files/records"
    params = {"filter": 'name="testfile.txt"'}
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    assert resp.status_code == 200, f"File query failed: {resp.text}"
    files = resp.json().get("items", [])
    assert files, "File entry not found in PocketBase."
    file_id = files[0]["id"]

    # Query PocketBase for rename log
    url = "http://127.0.0.1:8090/api/collections/rename_logs/records"
    params = {"filter": f'file_id="{file_id}"'}
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    assert resp.status_code == 200, f"RenameLog query failed: {resp.text}"
    logs = resp.json().get("items", [])
    assert logs, "RenameLog entry not found in PocketBase."
    log = logs[0]
    assert log["new_path"] == "/tmp/testfile.txt"
    assert log["event_type"] == "create"
