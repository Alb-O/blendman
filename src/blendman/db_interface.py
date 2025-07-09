"""
Main interface logic for DB operations and queries.

Exposes APIs for persisting and querying file/dir state and rename logs.
"""

from typing import List, Optional
from packages.pocketbase_backend.src.pocketbase.api import PocketBaseAPI
from packages.pocketbase_backend.src.pocketbase.auth import AuthClient
import structlog  # type: ignore
import os


class DBInterface:
    """
    Interface for all DB operations related to files, directories, and rename logs.
    """

    def __init__(self):
        self.logger = structlog.get_logger("DBInterface")
        self.auth_client = AuthClient()
        # Use admin credentials from env for initial login
        admin_email = os.environ.get("POCKETBASE_ADMIN_EMAIL")
        admin_password = os.environ.get("POCKETBASE_ADMIN_PASSWORD")
        if not admin_email or not admin_password:
            raise ValueError(
                "POCKETBASE_ADMIN_EMAIL and POCKETBASE_ADMIN_PASSWORD must be set in environment."
            )
        try:
            self.auth_client.login(admin_email, admin_password)
        except Exception as e:
            self.logger.error(f"Auth login failed: {e}")
            raise
        self.api = PocketBaseAPI()

    def persist_event(self, event: dict) -> None:
        """
        Persist a watcher event: update FileDir and insert RenameLog.
        """
        try:
            # Upsert file/dir record
            file_data = {
                "name": event["name"],
                "path": event["new_path"],
                "parent_id": event.get("parent_id"),
                "type": event["type"],
            }
            self.logger.info(f"[DBInterface] Creating file record: {file_data}")
            # Ensure token is valid before DB operation
            if not self.auth_client.get_token():
                admin_email = os.environ.get("POCKETBASE_ADMIN_EMAIL")
                admin_password = os.environ.get("POCKETBASE_ADMIN_PASSWORD")
                self.auth_client.login(admin_email, admin_password)
            try:
                file_record = self.api.collections.create("files", file_data)
                self.logger.info(f"[DBInterface] File record created: {file_record}")
            except Exception as e:
                self.logger.error(
                    f"[DBInterface] File record creation failed: {file_data} | Error: {e}"
                )
                raise
            # Insert rename log
            log_data = {
                "file_id": file_record["id"],
                "old_path": event.get("old_path", ""),
                "new_path": event["new_path"],
                "event_type": event["event_type"],
            }
            self.logger.info(f"[DBInterface] Creating rename log: {log_data}")
            try:
                log_record = self.api.collections.create("rename_logs", log_data)
                self.logger.info(f"[DBInterface] Rename log created: {log_record}")
            except Exception as e:
                self.logger.error(
                    f"[DBInterface] Rename log creation failed: {log_data} | Error: {e}"
                )
                raise
        except Exception as e:
            self.logger.error(f"DB persist_event failed: {event} | Error: {e}")

    def get_logs_for_file(self, file_id: str) -> List[dict]:
        """
        Fetch all logs for a given file/dir by file_id.
        """
        try:
            return self.api.collections.list(
                "rename_logs", filter={"file_id": file_id}, sort="timestamp"
            )
        except Exception as e:
            self.logger.error(f"DB get_logs_for_file failed: {file_id} | Error: {e}")
            return []

    def get_global_log(self) -> List[dict]:
        """
        Fetch all rename logs, ordered by timestamp.
        """
        try:
            return self.api.collections.list("rename_logs", sort="timestamp")
        except Exception as e:
            self.logger.error(f"DB get_global_log failed | Error: {e}")
            return []

    def get_file_state(self, file_id: str) -> Optional[dict]:
        """
        Fetch the current state of a file/dir by file_id.
        """
        try:
            return self.api.collections.get("files", file_id)
        except Exception as e:
            self.logger.error(f"DB get_file_state failed: {file_id} | Error: {e}")
            return None

    def get_file_history(self, file_id: str) -> List[dict]:
        """
        Fetch the full history (logs) for a file/dir by file_id.
        """
        return self.get_logs_for_file(file_id)
