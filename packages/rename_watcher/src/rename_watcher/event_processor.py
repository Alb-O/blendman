"""
Event correlation and rename/move detection for rename_watcher.
"""

from typing import Any, Dict, Optional, Callable, List
import os
import time

import structlog  # type: ignore

from .path_map import PathInodeMap


class EventProcessor:
    """
    Processes and correlates raw file system events to detect renames and moves, including
    recursive path updates for nested folders.
    """

    def flush(self) -> None:
        """
        Flush all pending create/delete events immediately, emitting them if not paired as moves.
        Useful for shutdown or test scenarios.
        """
        now = (
            time.monotonic() + self.DEBOUNCE_WINDOW + 1
        )  # Ensure all pending events are flushed
        self._flush_pending_events(now)

    def __init__(
        self,
        path_map: PathInodeMap,
        emit_event: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ) -> None:
        """
        Initialize the event processor.

        Args:
            path_map (PathInodeMap): The path-inode map for tracking file/folder paths.
            emit_event (Optional[Callable]): Callback to emit high-level events.
        """
        self._pending_deletes: Dict[str, float] = {}
        self._pending_creates: Dict[str, float] = {}
        self._pending_payloads: Dict[str, Dict[str, Any]] = {}
        self.path_map = path_map
        self.emit_event = emit_event

    DEBOUNCE_WINDOW = 0.5  # seconds

    def process(self, event: Dict[str, Any]) -> None:
        """
        Process a raw event and emit high-level events if detected.

        Args:
            event (Dict[str, Any]): Raw event from watcher. Must include 'type', 'src_path',
                and optionally 'dest_path'.
        """
        log = structlog.get_logger("EventProcessor")
        log.info("process called", pid=os.getpid(), event_data=event)
        event_type = event.get("type")
        src_path = event.get("src_path")
        dest_path = event.get("dest_path")

        if event_type in ("moved", "renamed") and src_path and dest_path:
            log.info(
                "process handling native move", src_path=src_path, dest_path=dest_path
            )
            self._handle_native_move(src_path, dest_path)
            return

        now = time.monotonic()

        if event_type == "deleted" and src_path:
            if self._handle_deleted_event(src_path, now):
                log.info("process handled deleted event", src_path=src_path)
                return

        if event_type == "created" and src_path:
            if self._handle_created_event(src_path, now):
                log.info("process handled created event", src_path=src_path)
                return

        self._flush_pending_events(now)

    def _handle_native_move(self, src_path: str, dest_path: str) -> None:
        """
        Handle a native move/rename event and emit high-level events for folder and descendants.

        Args:
            src_path (str): Source path.
            dest_path (str): Destination path.
        """
        log = structlog.get_logger("EventProcessor")
        log.info(
            "_handle_native_move called",
            pid=os.getpid(),
            src_path=src_path,
            dest_path=dest_path,
        )
        self.path_map.bulk_update_paths(src_path, dest_path)
        descendants = self.path_map.descendants(dest_path)
        for path, inode in descendants.items():
            if self.emit_event:
                payload: Dict[str, Any] = {
                    "path": path,
                    "inode": inode,
                    "old_parent": src_path,
                    "new_parent": dest_path,
                }
                log.info("_handle_native_move emitting descendant", payload=payload)
                self.emit_event("moved", payload)
        if self.emit_event:
            folder_inode = self.path_map.get_inode(dest_path)
            folder_payload: Dict[str, Any] = {
                "path": dest_path,
                "inode": folder_inode,
                "old_parent": src_path,
                "new_parent": dest_path,
            }
            log.info("_handle_native_move emitting folder", payload=folder_payload)
            self.emit_event("moved", folder_payload)

    def _handle_deleted_event(self, src_path: str, now: float) -> bool:
        """
        Handle a deleted event, check for possible paired create (move/rename), and emit events.

        Args:
            src_path (str): Source path.
            now (float): Current time.

        Returns:
            bool: True if handled as a move, False otherwise.
        """
        self._pending_deletes[src_path] = now
        self._pending_payloads[src_path] = {
            "path": src_path,
            "inode": self.path_map.get_inode(src_path),
        }
        for create_path, create_time in list(self._pending_creates.items()):
            if abs(now - create_time) < self.DEBOUNCE_WINDOW:
                if src_path.split("/")[-1] == create_path.split("/")[-1]:
                    if self.emit_event:
                        self.emit_event(
                            "moved",
                            {
                                "path": create_path,
                                "inode": self.path_map.get_inode(create_path),
                                "old_parent": src_path,
                                "new_parent": create_path,
                            },
                        )
                    del self._pending_creates[create_path]
                    del self._pending_deletes[src_path]
                    self._pending_payloads.pop(src_path, None)
                    return True
        return False

    def _handle_created_event(self, src_path: str, now: float) -> bool:
        """
        Handle a created event, check for possible paired delete (move/rename), and emit events.

        Args:
            src_path (str): Source path.
            now (float): Current time.

        Returns:
            bool: True if handled as a move, False otherwise.
        """
        self._pending_creates[src_path] = now
        self._pending_payloads[src_path] = {
            "path": src_path,
            "inode": self.path_map.get_inode(src_path),
        }
        for delete_path, delete_time in list(self._pending_deletes.items()):
            if abs(now - delete_time) < self.DEBOUNCE_WINDOW:
                if src_path.split("/")[-1] == delete_path.split("/")[-1]:
                    if self.emit_event:
                        self.emit_event(
                            "moved",
                            {
                                "path": src_path,
                                "inode": self.path_map.get_inode(src_path),
                                "old_parent": delete_path,
                                "new_parent": src_path,
                            },
                        )
                    del self._pending_deletes[delete_path]
                    del self._pending_creates[src_path]
                    self._pending_payloads.pop(delete_path, None)
                    return True
        return False

    def _flush_pending_events(self, now: float) -> None:
        """
        Flush all pending create and delete events that have exceeded the debounce window.

        Args:
            now (float): Current time.
        """
        to_delete: List[str] = []
        for path, t in self._pending_deletes.items():
            if now - t > self.DEBOUNCE_WINDOW:
                if self.emit_event:
                    self.emit_event(
                        "deleted", self._pending_payloads.get(path, {"path": path})
                    )
                to_delete.append(path)
        for path in to_delete:
            del self._pending_deletes[path]
            self._pending_payloads.pop(path, None)

        to_create: List[str] = []
        for path, t in self._pending_creates.items():
            if now - t > self.DEBOUNCE_WINDOW:
                if self.emit_event:
                    self.emit_event(
                        "created", self._pending_payloads.get(path, {"path": path})
                    )
                to_create.append(path)
        for path in to_create:
            del self._pending_creates[path]
            self._pending_payloads.pop(path, None)
