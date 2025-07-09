import pytest  # type: ignore
from unittest.mock import MagicMock
from blendman.db_interface import DBInterface


class DummyAPI:
    def __init__(self):
        self.collections = MagicMock()
        self.auth = MagicMock()


@pytest.fixture
def db(monkeypatch):
    monkeypatch.setattr("blendman.db_interface.PocketBaseAPI", lambda: DummyAPI())
    return DBInterface()


def test_persist_event_expected(db):
    event = {
        "name": "foo.txt",
        "new_path": "/root/foo.txt",
        "type": "file",
        "event_type": "create",
    }
    db.api.collections.create.return_value = {"id": "1"}
    db.persist_event(event)
    assert db.api.collections.create.call_count == 2


def test_get_logs_for_file_expected(db):
    db.api.collections.list.return_value = ["log1", "log2"]
    logs = db.get_logs_for_file("1")
    assert logs == ["log1", "log2"]


def test_get_global_log_expected(db):
    db.api.collections.list.return_value = ["log1", "log2"]
    logs = db.get_global_log()
    assert logs == ["log1", "log2"]


def test_get_file_state_expected(db):
    db.api.collections.get.return_value = {"id": "1", "name": "foo.txt"}
    state = db.get_file_state("1")
    assert state["name"] == "foo.txt"


def test_get_file_history_expected(db):
    db.api.collections.list.return_value = ["log1", "log2"]
    history = db.get_file_history("1")
    assert history == ["log1", "log2"]


def test_failure_persist_event(db, caplog):
    db.api.collections.create.side_effect = Exception("fail")
    with caplog.at_level("ERROR"):
        event = {
            "name": "foo.txt",
            "new_path": "/root/foo.txt",
            "type": "file",
            "event_type": "create",
        }
        db.persist_event(event)
    assert "DB persist_event failed" in caplog.text
