"""
Bridge between RenameWatcher events and DB operations.

Subscribes to RenameWatcher events and persists them using the DB interface.
"""

from packages.rename_watcher.src.rename_watcher.api import RenameWatcherAPI
from .db_interface import DBInterface
import structlog  # type: ignore


class WatcherBridge:
    """
    Bridge class to subscribe to watcher events and persist them in the DB.
    """

    def __init__(self, db_interface: DBInterface, path: str = None, matcher=None):
        self.db_interface = db_interface
        self.logger = structlog.get_logger("WatcherBridge")
        self.watcher = RenameWatcherAPI(path=path, matcher=matcher)

    def start(self):
        """
        Start subscribing to watcher events and start the watcher.
        """
        self.logger.info(
            "[WatcherBridge] Registering handle_event as watcher subscriber."
        )
        self.watcher.subscribe(self.handle_event)
        self.logger.info("[WatcherBridge] Starting watcher.")
        self.watcher.start()
        self.logger.info(
            "[WatcherBridge] Subscribed to watcher events and started watcher."
        )

    def handle_event(self, event: dict):
        import os

        self.logger.info(
            "[WatcherBridge] handle_event called", pid=os.getpid(), event_data=event
        )
        """
        Handle a watcher event and persist it using the DB interface.

        Args:
            event (dict): The watcher event.
        """
        self.logger.info(f"[WatcherBridge] Received event: {event}")
        try:
            # Transform event to match DBInterface.persist_event schema
            transformed = {}
            event_type = event.get("type")
            transformed["event_type"] = event_type
            # Path fields
            if event_type == "moved":
                transformed["name"] = (
                    event.get("path", "").split("/")[-1]
                    or event.get("path", "").split("\\")[-1]
                )
                transformed["new_path"] = event.get("new_parent") or event.get("path")
                transformed["old_path"] = event.get("old_parent") or ""
            else:
                transformed["name"] = (
                    event.get("path", "").split("/")[-1]
                    or event.get("path", "").split("\\")[-1]
                )
                transformed["new_path"] = event.get("path")
                transformed["old_path"] = event.get("old_path", "")
            # Type: file or dir (try to infer from inode or fallback to file)
            transformed["type"] = (
                event.get("file_type") or event.get("type_hint") or "file"
            )
            # Parent id (optional, not always available)
            if "parent_id" in event:
                transformed["parent_id"] = event["parent_id"]
            self.logger.info(f"[WatcherBridge] Transformed event for DB: {transformed}")
            self.db_interface.persist_event(transformed)
            self.logger.info(f"[WatcherBridge] Event persisted to DB: {transformed}")
        except Exception as e:
            self.logger.error(
                f"[WatcherBridge] Failed to persist watcher event: {event} | Error: {e}"
            )
