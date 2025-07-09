"""
Bridge between RenameWatcher events and DB operations.

Subscribes to RenameWatcher events and persists them using the DB interface.
"""

import os
import structlog  # type: ignore
from rename_watcher.api import RenameWatcherAPI
from pocketbase.exceptions import PocketBaseError
from .db_interface import DBInterface


class WatcherBridge:
    """Bridge class to subscribe to watcher events and persist them in the DB."""

    def __init__(
        self, db_interface: DBInterface, path: str | None = None, matcher=None
    ) -> None:
        """Initialize the bridge with the given DB interface and watcher settings."""
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

    def handle_event(self, event: dict) -> None:
        """Handle a watcher event and persist it using the DB interface."""
        self.logger.info(
            "[WatcherBridge] handle_event called", pid=os.getpid(), event_data=event
        )
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
        except PocketBaseError as exc:
            self.logger.error(
                "[WatcherBridge] Failed to persist watcher event",
                event_data=event,
                error=str(exc),
            )
