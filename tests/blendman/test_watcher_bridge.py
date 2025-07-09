import pytest  # type: ignore
from unittest.mock import MagicMock
from blendman.watcher_bridge import WatcherBridge


class DummyDBInterface:
    def __init__(self):
        self.persisted = []

    def persist_event(self, event):
        self.persisted.append(event)


class DummyWatcher:
    def __init__(self):
        self.subscribed = False
        self.callback = None

    def subscribe(self, cb):
        self.subscribed = True
        self.callback = cb

    def emit(self, event):
        if self.callback:
            self.callback(event)

    def start(self):
        pass


@pytest.fixture
def bridge():
    db = DummyDBInterface()
    bridge = WatcherBridge(db)
    bridge.watcher = DummyWatcher()
    return bridge, db


def test_expected_event(bridge):
    bridge, db = bridge
    bridge.start()
    event = {
        "name": "foo.txt",
        "new_path": "/root/foo.txt",
        "type": "file",
        "event_type": "create",
    }
    bridge.watcher.emit(event)
    assert db.persisted[0]["name"] == "foo.txt"


def test_edge_empty_event(bridge):
    bridge, db = bridge
    bridge.start()
    bridge.watcher.emit({})
    assert db.persisted == []


def test_failure_db_error(bridge, caplog):
    bridge, db = bridge
    bridge.start()
    db.persist_event = MagicMock(side_effect=Exception("fail"))
    with caplog.at_level("ERROR"):
        bridge.watcher.emit(
            {
                "name": "foo.txt",
                "new_path": "/root/foo.txt",
                "type": "file",
                "event_type": "create",
            }
        )
    assert "Failed to persist watcher event" in caplog.text
