"""
Core watcher logic for rename_watcher.
Wraps watchdog to monitor file and directory events recursively.
"""

# This module favors clarity over strict pylint limits
# pylint: disable=too-many-instance-attributes,too-many-arguments,too-many-positional-arguments

import os
import threading
import time
from typing import Any, Callable, Optional
import logging

from rich.console import Console

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    Observer = None  # type: ignore[assignment]
    FileSystemEventHandler = Any  # type: ignore[assignment,misc]

from .path_map import PathInodeMap
from .event_processor import EventProcessor

console = Console()
logger = logging.getLogger(__name__)


class Watcher:
    """
    Watches directories for file and directory events (create, delete, move, rename),
    and emits high-level events using PathInodeMap and EventProcessor.
    """

    def __init__(
        self,
        path: str,
        on_event: Optional[Callable[[Any], None]] = None,
        path_map: Optional[PathInodeMap] = None,
        event_processor: Optional[EventProcessor] = None,
        matcher: Optional[Callable[[str], bool]] = None,
    ) -> None:
        """
        Initialize the Watcher.

        Args:
            path (str): Directory path to watch.
            on_event (Optional[Callable[[Any], None]]): Callback for events.
            path_map (Optional[PathInodeMap]): PathInodeMap instance.
            event_processor (Optional[EventProcessor]): EventProcessor instance.
            matcher (Optional[Callable[[str], bool]]): Path matcher function.
        """
        self.path = path
        self.on_event = on_event
        self.matcher = matcher
        self._observer: Optional[Any] = None  # type: ignore
        self._thread: Optional[Any] = None  # type: ignore
        self._running = False
        self._path_map = path_map or PathInodeMap()
        self._event_processor = event_processor or EventProcessor(
            self._path_map, self._emit_high_level
        )

    def start(self) -> None:
        """
        Start the watcher and begin monitoring the directory.
        """
        if Observer is None:
            raise ImportError(
                "watchdog is required for file system watching. Please install it."
            )
        if self._observer is not None:
            return  # Already started
        event_handler = self._make_event_handler()
        observer = Observer()
        observer.schedule(event_handler, self.path, recursive=True)
        observer.start()
        self._observer = observer
        self._running = True
        thread = threading.Thread(target=self._run_loop, daemon=True)
        thread.start()
        self._thread = thread

    def stop(self) -> None:
        """
        Stop the watcher and clean up resources.
        """
        self._running = False
        if self._observer is not None:
            self._observer.stop()
            self._observer.join()
            self._observer = None
        if self._thread is not None:
            self._thread.join(timeout=1)
            self._thread = None

    def _run_loop(self) -> None:
        """
        Internal run loop for the watcher thread.
        """
        try:
            while self._running:
                time.sleep(0.2)
        except KeyboardInterrupt:
            self.stop()

    def _make_event_handler(self) -> Any:
        """
        Create and return a file system event handler.

        Returns:
            Any: An event handler instance.
        """
        parent = self

        class Handler(FileSystemEventHandler):  # type: ignore[misc]
            """
            Internal event handler for file system events.
            """

            def on_created(self, event: Any) -> None:
                """Handle file/directory creation event."""
                logger.debug("Raw event created", path=event.src_path)
                # Accessing protected member is fine in this internal callback.
                parent._handle_raw_event(  # pylint: disable=protected-access
                    {
                        "type": "created",
                        "src_path": getattr(event, "src_path", None),
                        "is_directory": getattr(event, "is_directory", False),
                    }
                )

            def on_deleted(self, event: Any) -> None:
                """Handle file/directory deletion event."""
                logger.debug("Raw event deleted", path=event.src_path)
                parent._handle_raw_event(  # pylint: disable=protected-access
                    {
                        "type": "deleted",
                        "src_path": getattr(event, "src_path", None),
                        "is_directory": getattr(event, "is_directory", False),
                    }
                )

            def on_moved(self, event: Any) -> None:
                """Handle file/directory move event."""
                logger.debug(
                    "Raw event moved",
                    src=event.src_path,
                    dest=getattr(event, "dest_path", None),
                )
                parent._handle_raw_event(  # pylint: disable=protected-access
                    {
                        "type": "moved",
                        "src_path": getattr(event, "src_path", None),
                        "dest_path": getattr(event, "dest_path", None),
                        "is_directory": getattr(event, "is_directory", False),
                    }
                )

            def on_modified(self, _event: Any) -> None:
                """Handle file/directory modification event (optional)."""
                # No-op: modification events are not handled.
                return None

        return Handler()

    def _handle_raw_event(self, event: dict[str, Any]) -> None:
        """
        Handle a raw file system event.

        Args:
            event (dict[str, Any]): The event dictionary.
        """
        logger.debug("Handling raw event", event=event)
        # Optionally filter with matcher
        path = event.get("src_path") or event.get("dest_path")
        if self.matcher and path and not self.matcher(path):
            logger.debug("Event filtered by matcher", path=path)
            return
        # Track inodes for created files
        if event["type"] == "created" and not event.get("is_directory"):
            try:
                inode = os.stat(event["src_path"]).st_ino
                self._path_map.add(event["src_path"], inode)
                logger.debug(
                    "Added inode mapping",
                    path=event["src_path"],
                    inode=inode,
                )
            except Exception as exc:  # pylint: disable=broad-exception-caught
                # Broad exception is justified: stat may fail for race conditions
                # so we do not break the event flow.
                logger.warning("Failed to stat created file", error=str(exc))
        self._event_processor.process(event)

    def _emit_high_level(self, _event_type: str, _payload: dict[str, Any]) -> None:
        """
        Callback for emitting high-level events (legacy/test only).

        Args:
            event_type (str): The type of event.
            payload (dict[str, Any]): The event payload.
        """
        # This method is only used as a callback for EventProcessor in legacy/test cases.
        # In production, high-level event emission should be handled by
        # RenameWatcherAPI._emit_high_level only. Do not emit or print here.
        # All high-level event routing must go through the API for correct
        # subscriber delivery.
        return None
