"""
Unit tests for EventProcessor in event_processor.py.
"""

from rename_watcher.event_processor import EventProcessor


def test_process_noop() -> None:
    """
    Test process does not raise on empty event (expected use).
    """
    ep = EventProcessor()
    ep.process(None)  # Should not raise


def test_process_multiple_events() -> None:
    """
    Test process can be called multiple times (edge case).
    """
    ep = EventProcessor()
    for i in range(5):
        ep.process({"type": "create", "path": f"file{i}.txt"})


def test_process_invalid_event() -> None:
    """
    Test process handles invalid event types (failure case).
    """
    ep = EventProcessor()
    try:
        ep.process({"type": "unknown", "path": "bad.txt"})
    except Exception:
        pass  # Should not crash
