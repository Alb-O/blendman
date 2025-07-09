"""
Main interface logic for DB operations and queries.

Exposes APIs for persisting and querying file/dir state and rename logs.
"""

from typing import List, Optional
from pocketbase.api import PocketBaseAPI
from dotenv import load_dotenv  # type: ignore
import os
import logging


class DBInterface:
    """
    Interface for all DB operations related to files, directories, and rename logs.
    """

    def __init__(self):
        load_dotenv()
        self.api = PocketBaseAPI()
        self.logger = logging.getLogger("DBInterface")
        self.api.auth.login(
            email=os.getenv("POCKETBASE_ADMIN_EMAIL"),
            password=os.getenv("POCKETBASE_ADMIN_PASSWORD"),
        )

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
            file_record = self.api.collections.create("files", file_data)
            # Insert rename log
            log_data = {
                "file_id": file_record["id"],
                "old_path": event.get("old_path", ""),
                "new_path": event["new_path"],
                "event_type": event["event_type"],
            }
            self.api.collections.create("rename_logs", log_data)
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
