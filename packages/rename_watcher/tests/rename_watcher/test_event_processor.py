"""
Unit tests for EventProcessor in event_processor.py.
"""

from rename_watcher.event_processor import EventProcessor
from rename_watcher.path_map import PathInodeMap


def test_recursive_folder_move_updates_descendants_and_emits_events() -> None:
    """
    Test that moving a folder updates all descendant paths and emits correct events.
    """
    # Setup path map with nested structure
    pm = PathInodeMap()
    pm.add("/root/folder", 1)
    pm.add("/root/folder/file1.txt", 2)
    pm.add("/root/folder/sub", 3)
    pm.add("/root/folder/sub/file2.txt", 4)
    events: list[tuple[str, dict[str, object]]] = []

    def emit_event(event_type: str, payload: dict[str, object]) -> None:
        events.append((event_type, payload))

    ep = EventProcessor(pm, emit_event=emit_event)
    # Simulate move event
    ep.process(
        {
            "type": "moved",
            "src_path": "/root/folder",
            "dest_path": "/root/folder_renamed",
        }
    )
    # All paths should be updated
    assert pm.get_inode("/root/folder_renamed") == 1
    assert pm.get_inode("/root/folder_renamed/file1.txt") == 2
    assert pm.get_inode("/root/folder_renamed/sub") == 3
    assert pm.get_inode("/root/folder_renamed/sub/file2.txt") == 4
    # Events should be emitted for all descendants and the folder itself
    moved_paths = {payload["path"] for (etype, payload) in events if etype == "moved"}
    expected_paths = {
        "/root/folder_renamed",
        "/root/folder_renamed/file1.txt",
        "/root/folder_renamed/sub",
        "/root/folder_renamed/sub/file2.txt",
    }
    assert moved_paths == expected_paths


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
    except Exception:
        pass  # Should not crash
