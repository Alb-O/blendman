"""
Bridge between RenameWatcher events and DB operations.

Subscribes to RenameWatcher events and persists them using the DB interface.
"""

from packages.rename_watcher.src.rename_watcher.api import RenameWatcherAPI
from .db_interface import DBInterface
import logging


class WatcherBridge:
    """
    Bridge class to subscribe to watcher events and persist them in the DB.
    """

    def __init__(self, db_interface: DBInterface):
        self.db_interface = db_interface
        self.watcher = RenameWatcherAPI()
        self.logger = logging.getLogger("WatcherBridge")

    def start(self):
        """
        Start subscribing to watcher events.
        """
        self.watcher.subscribe(self.handle_event)
        self.logger.info("WatcherBridge subscribed to watcher events.")

    def handle_event(self, event: dict):
        """
        Handle a watcher event and persist it using the DB interface.

        Args:
                event (dict): The watcher event.
        """
        try:
            self.db_interface.persist_event(event)
        except Exception as e:
            self.logger.error(f"Failed to persist watcher event: {event} | Error: {e}")
