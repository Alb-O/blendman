import pytest  # type: ignore
from datetime import datetime
from blendman.models import FileDirModel, RenameLogModel


class TestFileDirModel:
    def test_expected(self):
        obj = FileDirModel(
            id="1",
            name="foo.txt",
            path="/root/foo.txt",
            parent_id=None,
            type="file",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert obj.name == "foo.txt"
        assert obj.type == "file"

    def test_edge_unicode(self):
        obj = FileDirModel(
            id="2",
            name="файл.txt",
            path="/root/файл.txt",
            parent_id=None,
            type="file",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert obj.name == "файл.txt"

    def test_failure_missing_field(self):
        from pydantic import ValidationError  # type: ignore

        with pytest.raises(ValidationError):
            FileDirModel(
                id="3", name="bar", path="/bar", type="file", created_at=datetime.now()
            )


class TestRenameLogModel:
    def test_expected(self):
        obj = RenameLogModel(
            id="1",
            file_id="1",
            old_path="/root/foo.txt",
            new_path="/root/bar.txt",
            event_type="rename",
            timestamp=datetime.now(),
        )
        assert obj.event_type == "rename"

    def test_edge_event_type(self):
        obj = RenameLogModel(
            id="2",
            file_id="1",
            old_path="/root/foo.txt",
            new_path="/root/bar.txt",
            event_type="move",
            timestamp=datetime.now(),
        )
        assert obj.event_type == "move"

    def test_failure_invalid_event_type(self):
        with pytest.raises(ValueError):
            RenameLogModel(
                id="3",
                file_id="1",
                old_path="/root/foo.txt",
                new_path="/root/bar.txt",
                event_type="invalid",
                timestamp=datetime.now(),
            )
