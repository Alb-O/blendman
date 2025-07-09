"""
Main interface logic for DB operations and queries.

Exposes APIs for persisting and querying file/dir state and rename logs.
"""

from typing import List, Optional
import os

import structlog  # type: ignore

from pocketbase.api import PocketBaseAPI
from pocketbase.auth import AuthClient
from pocketbase.exceptions import PocketBaseError


class DBInterface:
    """
    Interface for all DB operations related to files, directories, and rename logs.
    """

    def __init__(self):
        self.logger = structlog.get_logger("DBInterface")
        self.auth_client = AuthClient()
        self.api = PocketBaseAPI()
        self._ensure_auth()

    def _ensure_auth(self) -> None:
        """Ensure the AuthClient is logged in, prompting if needed."""
        if self.auth_client.is_authenticated():
            return
        admin_email = os.environ.get("POCKETBASE_ADMIN_EMAIL")
        admin_password = os.environ.get("POCKETBASE_ADMIN_PASSWORD")
        if not admin_email or not admin_password:
            admin_email = input("PocketBase admin email: ")
            import getpass

            admin_password = getpass.getpass("PocketBase admin password: ")
        try:
            self.auth_client.login(admin_email, admin_password)
        except PocketBaseError as exc:
            self.logger.error("Auth login failed", error=str(exc))
            raise

    def persist_event(self, event: dict) -> None:
        """
        Persist a watcher event: update FileDir and insert RenameLog.
        """
        # Upsert file/dir record
        file_data = {
            "name": event["name"],
            "path": event["new_path"],
            "parent_id": event.get("parent_id"),
            "type": event["type"],
        }
        self.logger.info("[DBInterface] Creating file record", data=file_data)
        if not self.auth_client.is_authenticated():
            self._ensure_auth()
        try:
            file_record = self.api.collections.create(  # pylint: disable=no-member
                "files", file_data
            )
            self.logger.info("[DBInterface] File record created", record=file_record)
        except PocketBaseError as exc:
            self.logger.error(
                "[DBInterface] File record creation failed",
                data=file_data,
                error=str(exc),
            )
            raise

        # Insert rename log
        log_data = {
            "file_id": file_record["id"],
            "old_path": event.get("old_path", ""),
            "new_path": event["new_path"],
            "event_type": event["event_type"],
        }
        self.logger.info("[DBInterface] Creating rename log", data=log_data)
        try:
            log_record = self.api.collections.create(  # pylint: disable=no-member
                "rename_logs", log_data
            )
            self.logger.info("[DBInterface] Rename log created", record=log_record)
        except PocketBaseError as exc:
            self.logger.error(
                "[DBInterface] Rename log creation failed",
                data=log_data,
                error=str(exc),
            )
            raise

    def get_logs_for_file(self, file_id: str) -> List[dict]:
        """
        Fetch all logs for a given file/dir by file_id.
        """
        try:
            return self.api.collections.list(  # pylint: disable=no-member
                "rename_logs", filter={"file_id": file_id}, sort="timestamp"
            )
        except PocketBaseError as exc:
            self.logger.error(
                "DB get_logs_for_file failed", file_id=file_id, error=str(exc)
            )
            return []

    def get_global_log(self) -> List[dict]:
        """
        Fetch all rename logs, ordered by timestamp.
        """
        try:
            return self.api.collections.list(  # pylint: disable=no-member
                "rename_logs", sort="timestamp"
            )
        except PocketBaseError as exc:
            self.logger.error("DB get_global_log failed", error=str(exc))
            return []

    def get_file_state(self, file_id: str) -> Optional[dict]:
        """
        Fetch the current state of a file/dir by file_id.
        """
        try:
            return self.api.collections.get(  # pylint: disable=no-member
                "files", file_id
            )
        except PocketBaseError as exc:
            self.logger.error(
                "DB get_file_state failed", file_id=file_id, error=str(exc)
            )
            return None

    def get_file_history(self, file_id: str) -> List[dict]:
        """
        Fetch the full history (logs) for a file/dir by file_id.
        """
        return self.get_logs_for_file(file_id)
