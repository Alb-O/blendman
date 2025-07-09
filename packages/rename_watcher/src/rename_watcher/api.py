"""
Public API for rename_watcher.
"""

from typing import Callable, Any, List, Optional, Dict
import os
import structlog  # type: ignore
from .watcher import Watcher
from .path_map import PathInodeMap
from .event_processor import EventProcessor


class RenameWatcherAPI:
    """
    Public API for subscribing to high-level file system events.
    Wires up Watcher, PathInodeMap, and EventProcessor.
    """

    def __init__(
        self,
        path: Optional[str] = None,
        matcher: Optional[Callable[[str], bool]] = None,
    ) -> None:
        import structlog  # type: ignore

        self.logger = structlog.get_logger("RenameWatcherAPI")
        self._subscribers: List[Callable[[Any], None]] = []
        self._matcher = matcher
        self._path = path or os.getcwd()
        self._path_map = PathInodeMap()
        self._event_processor = EventProcessor(self._path_map, self._emit_high_level)
        # Force the watcher to use the API's event processor, not its own
        self._watcher = Watcher(
            self._path,
            on_event=self._on_raw_event,
            path_map=self._path_map,
            event_processor=self._event_processor,
            matcher=self._matcher,
        )
        self._watcher_started = False

    def start(self):
        """
        Start the watcher if it is not already started.
        """
        if not self._watcher_started:
            self._watcher.start()
            self._watcher_started = True

    def stop(self):
        """
        Stop the watcher if it is running.
        """
        if self._watcher_started:
            self._watcher.stop()
            self._watcher_started = False

    def subscribe(self, callback: Callable[[Any], None]) -> None:
        """
        Subscribe to high-level events (on_rename, on_move, etc.).
        """
        self._subscribers.append(callback)
        self.logger.info(
            "Subscriber registered",
            callback=repr(callback),
            total_subscribers=len(self._subscribers),
        )

    def emit(self, event: Any) -> None:
        """
        Emit an event to all subscribers (manual trigger, rarely used).
        """
        self._emit_high_level(event.get("type", "unknown"), event)

    def _emit_high_level(self, event_type: str, payload: Dict[str, Any]):
        """
        Emit a high-level event to all subscribers.

        Args:
            event_type (str): The type of event.
            payload (Dict[str, Any]): The event payload.
        """
        # Do not mutate the event dict; pass as-is to subscribers
        self.logger.info(
            "_emit_high_level called",
            pid=os.getpid(),
            event_type=event_type,
            payload=payload.copy() if hasattr(payload, "copy") else payload,
            subscribers=[repr(cb) for cb in self._subscribers],
            n_subscribers=len(self._subscribers),
        )
        for cb in self._subscribers:
            try:
                self.logger.info(
                    "Calling subscriber", subscriber=repr(cb), event_payload=payload
                )
                cb(payload)
            except Exception as e:
                # Broad exception is justified here to prevent a single subscriber from breaking the event chain.
                self.logger.error(
                    "Subscriber callback failed",
                    subscriber=repr(cb),
                    error=str(e),
                    event_payload=payload,
                )

    def _on_raw_event(self, event: Dict[str, Any]):
        """
        Handle a raw event from the watcher, filter, and process it.

        Args:
            event (Dict[str, Any]): The raw event data.
        """
        log = structlog.get_logger("RenameWatcherAPI")
        log.info("_on_raw_event called", pid=os.getpid(), event_data=event)
        # Optionally filter with matcher
        path = event.get("src_path") or event.get("dest_path")
        if self._matcher and path and not self._matcher(path):
            log.info("_on_raw_event filtered by matcher", path=path)
            return
        # Track inodes for created files
        if event["type"] == "created" and not event.get("is_directory"):
            try:
                inode = os.stat(event["src_path"]).st_ino
                self._path_map.add(event["src_path"], inode)
            except Exception:
                # Broad exception is justified here to avoid breaking event flow on stat failure.
                log.warning(
                    "_on_raw_event failed to stat created file",
                    src_path=event["src_path"],
                )
        self._event_processor.process(event)
