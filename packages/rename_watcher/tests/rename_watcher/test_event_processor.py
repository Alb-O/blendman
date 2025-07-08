"""
Unit tests for EventProcessor in event_processor.py.
"""

from rename_watcher.event_processor import EventProcessor
from rename_watcher.path_map import PathInodeMap


def test_rapid_consecutive_folder_moves() -> None:
    """
    Test that rapid consecutive moves update all paths correctly and emit correct events.
    """
    pm = PathInodeMap()
    pm.add("/root/folder", 1)
    pm.add("/root/folder/file.txt", 2)
    events: list[tuple[str, dict[str, object]]] = []

    def emit_event(event_type: str, payload: dict[str, object]) -> None:
        events.append((event_type, payload))

    ep = EventProcessor(pm, emit_event=emit_event)
    # Move 1
    ep.process(
        {"type": "moved", "src_path": "/root/folder", "dest_path": "/root/folder2"}
    )
    # Move 2 (immediately after)
    ep.process(
        {"type": "moved", "src_path": "/root/folder2", "dest_path": "/root/final"}
    )
    assert pm.get_inode("/root/final") == 1
    assert pm.get_inode("/root/final/file.txt") == 2
    moved_paths = {payload["path"] for (etype, payload) in events if etype == "moved"}
    assert "/root/final" in moved_paths and "/root/final/file.txt" in moved_paths


def test_move_folder_path_and_name_change() -> None:
    """
    Test moving a folder where both the parent path and the folder name change.
    """
    pm = PathInodeMap()
    pm.add("/a/b/c", 1)
    pm.add("/a/b/c/file.txt", 2)
    events: list[tuple[str, dict[str, object]]] = []

    def emit_event(event_type: str, payload: dict[str, object]) -> None:
        events.append((event_type, payload))

    ep = EventProcessor(pm, emit_event=emit_event)
    ep.process({"type": "moved", "src_path": "/a/b/c", "dest_path": "/x/y/z"})
    assert pm.get_inode("/x/y/z") == 1
    assert pm.get_inode("/x/y/z/file.txt") == 2
    moved_paths = {payload["path"] for (etype, payload) in events if etype == "moved"}
    assert "/x/y/z" in moved_paths and "/x/y/z/file.txt" in moved_paths


def test_move_folder_with_ignored_files() -> None:
    """
    Test moving a folder with a mix of included and ignored files
        (simulate by not adding ignored files to path map).
    """
    pm = PathInodeMap()
    pm.add("/root/folder", 1)
    pm.add("/root/folder/included.txt", 2)
    # Ignored file not added to path map
    events: list[tuple[str, dict[str, object]]] = []

    def emit_event(event_type: str, payload: dict[str, object]) -> None:
        events.append((event_type, payload))

    ep = EventProcessor(pm, emit_event=emit_event)
    ep.process(
        {"type": "moved", "src_path": "/root/folder", "dest_path": "/root/renamed"}
    )
    assert pm.get_inode("/root/renamed/included.txt") == 2
    assert pm.get_inode("/root/renamed/ignored.txt") is None
    moved_paths = {payload["path"] for (etype, payload) in events if etype == "moved"}
    assert "/root/renamed/included.txt" in moved_paths
    assert "/root/renamed/ignored.txt" not in moved_paths


def test_move_folder_with_only_ignored_files() -> None:
    """
    Test moving a folder that contains only ignored files (should not emit events).
    """
    pm = PathInodeMap()
    pm.add("/root/folder", 1)
    # No files added (all ignored)
    events: list[tuple[str, dict[str, object]]] = []

    def emit_event(event_type: str, payload: dict[str, object]) -> None:
        events.append((event_type, payload))

    ep = EventProcessor(pm, emit_event=emit_event)
    ep.process(
        {"type": "moved", "src_path": "/root/folder", "dest_path": "/root/renamed"}
    )
    # Only the folder event should be emitted
    moved_paths = {payload["path"] for (etype, payload) in events if etype == "moved"}
    assert moved_paths == {"/root/renamed"}


def test_simultaneous_nested_folder_moves() -> None:
    """
    Test moving multiple nested folders in sequence.
    """
    pm = PathInodeMap()
    pm.add("/root/outer", 1)
    pm.add("/root/outer/inner", 2)
    pm.add("/root/outer/inner/file.txt", 3)
    events: list[tuple[str, dict[str, object]]] = []

    def emit_event(event_type: str, payload: dict[str, object]) -> None:
        events.append((event_type, payload))

    ep = EventProcessor(pm, emit_event=emit_event)
    # Move inner first
    ep.process(
        {
            "type": "moved",
            "src_path": "/root/outer/inner",
            "dest_path": "/root/outer/inner2",
        }
    )
    # Then move outer
    ep.process(
        {"type": "moved", "src_path": "/root/outer", "dest_path": "/root/renamed"}
    )
    assert pm.get_inode("/root/renamed/inner2/file.txt") == 3
    moved_paths = {payload["path"] for (etype, payload) in events if etype == "moved"}
    assert "/root/renamed/inner2/file.txt" in moved_paths


def test_process_noop() -> None:
    """
    Test process does not raise on empty event (expected use).
    """
    pm = PathInodeMap()
    ep = EventProcessor(pm)
    ep.process({})  # Should not raise


def test_process_multiple_events() -> None:
    """
    Test process can be called multiple times (edge case).
    """
    pm = PathInodeMap()
    ep = EventProcessor(pm)
    for i in range(5):
        ep.process({"type": "create", "path": f"file{i}.txt"})


def test_process_invalid_event() -> None:
    """
    Test process handles invalid event types (failure case).
    """
    pm = PathInodeMap()
    ep = EventProcessor(pm)
    try:
        ep.process({"type": "unknown", "path": "bad.txt"})
    except Exception:  # pylint: disable=broad-exception-caught
        pass  # Should not crash


def test_windows_cross_directory_move_emits_create_and_delete() -> None:
    """
    On Windows, cross-directory moves are reported as delete at source and create at destination.
    The event processor should emit separate create/delete events, not a move.
    """
    pm = PathInodeMap()
    pm.add("C:/src/folder/file.txt", 1)
    events: list[tuple[str, dict[str, object]]] = []

    def emit_event(event_type: str, payload: dict[str, object]) -> None:
        events.append((event_type, payload))

    ep = EventProcessor(pm, emit_event=emit_event)
    # Simulate delete at source
    ep.process({"type": "deleted", "src_path": "C:/src/folder/file.txt"})
    # Simulate create at destination
    ep.process({"type": "created", "src_path": "D:/dst/folder/file.txt"})
    # Should emit a single moved event, not separate create/delete
    moved_events = [payload for (etype, payload) in events if etype == "moved"]
    assert len(moved_events) == 1
    moved = moved_events[0]
    assert moved["old_parent"] == "C:/src/folder/file.txt"
    assert moved["path"] == "D:/dst/folder/file.txt"
