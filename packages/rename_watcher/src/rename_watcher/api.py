"""
Public API for rename_watcher.
"""

from typing import Callable, Any, List


class RenameWatcherAPI:
    """
    Public API for subscribing to high-level file system events.
    """

    def __init__(self) -> None:
        self._subscribers: List[Callable[[Any], None]] = []

    def subscribe(self, callback: Callable[[Any], None]) -> None:
        """
        Subscribe to high-level events (on_rename, on_move, etc.).

        Args:
            callback (Callable[[Any], None]): Callback function for events.
        """
        self._subscribers.append(callback)

    def emit(self, event: Any) -> None:
        """
        Emit an event to all subscribers.
        """
        for cb in self._subscribers:
            cb(event)
