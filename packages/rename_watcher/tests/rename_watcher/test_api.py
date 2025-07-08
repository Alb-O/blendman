"""
Unit tests for RenameWatcherAPI in api.py.
"""

from rename_watcher.api import RenameWatcherAPI


def test_subscribe_and_emit() -> None:
    """
    Test subscribing to events and receiving emitted events (expected use).
    """
    api = RenameWatcherAPI()
    received: list[object] = []

    def cb(event: object) -> None:
        received.append(event)

    api.subscribe(cb)
    api.emit({"type": "rename", "src": "a.txt", "dst": "b.txt"})
    assert received == [{"type": "rename", "src": "a.txt", "dst": "b.txt"}]


def test_emit_no_subscribers() -> None:
    """
    Test emitting an event with no subscribers (edge case).
    """
    api = RenameWatcherAPI()
    # Should not raise
    api.emit({"type": "delete", "src": "a.txt"})


def test_subscribe_multiple() -> None:
    """
    Test multiple subscribers receive events (failure case: one raises).
    """
    api = RenameWatcherAPI()
    received1: list[object] = []
    received2: list[object] = []

    def cb1(event: object) -> None:
        received1.append(event)

    def cb2(event: object) -> None:
        received2.append(event)
        raise Exception("fail")  # pylint: disable=broad-exception-raised

    api.subscribe(cb1)
    api.subscribe(cb2)
    try:
        api.emit({"type": "move", "src": "a.txt", "dst": "b.txt"})
    except Exception:  # pylint: disable=broad-exception-caught
        # In test context, broad exception is justified to catch all errors
        pass
    assert received1 == [{"type": "move", "src": "a.txt", "dst": "b.txt"}]
    assert received2 == [{"type": "move", "src": "a.txt", "dst": "b.txt"}]
