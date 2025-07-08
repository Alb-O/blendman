"""
Event correlation and rename/move detection for rename_watcher.
"""

from typing import Any, Dict, Optional, Callable

from .path_map import PathInodeMap


class EventProcessor:
    """
    Processes and correlates raw file system events to detect renames and moves, including recursive path updates for nested folders.
    """

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
        self._pending_events: Dict[str, Any] = {}
        self.path_map = path_map
        self.emit_event = emit_event

    def process(self, event: Dict[str, Any]) -> None:
        """
        Process a raw event and emit high-level events if detected.

        Args:
            event (Dict[str, Any]): Raw event from watcher. Must include 'type', 'src_path', and optionally 'dest_path'.
        """
        event_type = event.get("type")
        src_path = event.get("src_path")
        dest_path = event.get("dest_path")

        # Detect folder move/rename
        if event_type in ("moved", "renamed") and src_path and dest_path:
            # Update all descendants in the path map
            self.path_map.bulk_update_paths(src_path, dest_path)
            # Emit high-level events for all affected descendants
            descendants = self.path_map.descendants(dest_path)
            for path, inode in descendants.items():
                if self.emit_event:
                    self.emit_event(
                        "moved",
                        {
                            "path": path,
                            "inode": inode,
                            "old_parent": src_path,
                            "new_parent": dest_path,
                        },
                    )
            # Emit event for the folder itself
            if self.emit_event:
                folder_inode = self.path_map.get_inode(dest_path)
                self.emit_event(
                    "moved",
                    {
                        "path": dest_path,
                        "inode": folder_inode,
                        "old_parent": src_path,
                        "new_parent": dest_path,
                    },
                )
        # ...existing code for other event types (create, delete, etc.) can be added here...
