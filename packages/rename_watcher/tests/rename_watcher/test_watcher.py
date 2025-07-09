"""
Unit tests for Watcher in watcher.py (stub, as actual file watching requires integration tests).
"""

# pylint: disable=import-outside-toplevel

from rename_watcher.watcher import Watcher


import tempfile


def test_init() -> None:
    """
    Test Watcher can be initialized (expected use).
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        w = Watcher(tmpdir, on_event=None)
        assert w.path == tmpdir
        assert w.on_event is None


def test_start_stop() -> None:
    """
    Test start and stop methods raise NotImplementedError on base class (edge case).
    """
    import pytest  # type: ignore

    with tempfile.TemporaryDirectory() as tmpdir:
        w = Watcher(tmpdir)
        with pytest.raises(NotImplementedError):
            w.start()
        with pytest.raises(NotImplementedError):
            w.stop()


def test_on_event_callback() -> None:
    """
    Test on_event callback is stored and callable (failure case: callback raises).
    """
    called = {}

    def cb(event: object) -> None:
        called["event"] = event
        raise Exception("fail")  # pylint: disable=broad-exception-raised

    with tempfile.TemporaryDirectory() as tmpdir:
        w = Watcher(tmpdir, on_event=cb)
        try:
            assert w.on_event is not None
            w.on_event({"type": "test"})
        except Exception:  # pylint: disable=broad-exception-caught
            # In test context, broad exception is justified to catch all errors
            pass
        assert called["event"] == {"type": "test"}
