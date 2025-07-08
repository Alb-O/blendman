"""
Core watcher logic for rename_watcher.
Wraps watchdog to monitor file and directory events recursively.
"""

from typing import Optional, Callable, Any


class Watcher:
    """
    Watches directories for file and directory events (create, delete, move, rename).
    """

    def __init__(self, path: str, on_event: Optional[Callable[[Any], None]] = None):
        """
        Initialize the watcher.

        Args:
            path (str): Directory to watch.
            on_event (Optional[Callable]): Callback for raw events.
        """
        self.path = path
        self.on_event = on_event

    def start(self) -> None:
        """
        Start watching the directory.
        """
        pass

    def stop(self) -> None:
        """
        Stop watching the directory.
        """
        pass
