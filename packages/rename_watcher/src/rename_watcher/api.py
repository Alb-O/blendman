"""
Public API for rename_watcher.
"""


from typing import Callable, Any, List, Optional
import os
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
        self._subscribers: List[Callable[[Any], None]] = []
        self._matcher = matcher
        self._path = path or os.getcwd()
        self._path_map = PathInodeMap()
        self._event_processor = EventProcessor(self._path_map, self._emit_high_level)
        self._watcher = Watcher(self._path, self._on_raw_event)
        self._watcher_started = False

    def start(self):
        if not self._watcher_started:
            print(f"[RenameWatcherAPI] Starting watcher on {self._path}")
            self._watcher.start()
            self._watcher_started = True

    def stop(self):
        if self._watcher_started:
            print(f"[RenameWatcherAPI] Stopping watcher on {self._path}")
            self._watcher.stop()
            self._watcher_started = False

    def subscribe(self, callback: Callable[[Any], None]) -> None:
        print(f"[RenameWatcherAPI] Subscribing callback: {callback}")
        self._subscribers.append(callback)

    def emit(self, event: Any) -> None:
        print(f"[RenameWatcherAPI] Emitting event to subscribers: {event}")
        for cb in self._subscribers:
            cb(event)

    def _emit_high_level(self, event_type: str, payload: dict):
        payload = dict(payload)
        payload["type"] = event_type
        print(f"[RenameWatcherAPI] High-level event: {payload}")
        for cb in self._subscribers:
            cb(payload)

    def _on_raw_event(self, event: dict):
        print(f"[RenameWatcherAPI] Raw event received: {event}")
        # Optionally filter with matcher
        path = event.get("src_path") or event.get("dest_path")
        if self._matcher and path and not self._matcher(path):
            print(f"[RenameWatcherAPI] Event filtered by matcher: {path}")
            return
        # Track inodes for created files
        if event["type"] == "created" and not event.get("is_directory"):
            try:
                inode = os.stat(event["src_path"]).st_ino
                self._path_map.add(event["src_path"], inode)
                print(f"[RenameWatcherAPI] Added inode mapping: {event['src_path']} -> {inode}")
            except Exception as e:
                print(f"[RenameWatcherAPI] Failed to stat created file: {e}")
        self._event_processor.process(event)
