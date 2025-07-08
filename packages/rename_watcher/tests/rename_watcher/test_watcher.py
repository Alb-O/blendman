"""
Unit tests for Watcher in watcher.py (stub, as actual file watching requires integration tests).
"""

from rename_watcher.watcher import Watcher


def test_init() -> None:
    """
    Test Watcher can be initialized (expected use).
    """
    w = Watcher("/tmp", on_event=None)
    assert w.path == "/tmp"
    assert w.on_event is None


def test_start_stop() -> None:
    """
    Test start and stop methods exist (edge case).
    """
    w = Watcher("/tmp")
    w.start()
    w.stop()


def test_on_event_callback() -> None:
    """
    Test on_event callback is stored and callable (failure case: callback raises).
    """
    called = {}

    def cb(event: object) -> None:
        called["event"] = event
        raise Exception("fail")

    w = Watcher("/tmp", on_event=cb)
    try:
        assert w.on_event is not None
        w.on_event({"type": "test"})
    except Exception:
        pass
    assert called["event"] == {"type": "test"}
