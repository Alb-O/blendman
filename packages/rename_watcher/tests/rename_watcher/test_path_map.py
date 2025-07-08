"""
Unit tests for PathInodeMap in path_map.py.
"""

from rename_watcher.path_map import PathInodeMap


def test_add_and_get_inode_and_path() -> None:
    """
    Test adding and retrieving path-inode mappings (expected use).
    """
    m = PathInodeMap()
    m.add("/tmp/foo.txt", 123)
    assert m.get_inode("/tmp/foo.txt") == 123
    assert m.get_path(123) == "/tmp/foo.txt"


def test_get_inode_missing() -> None:
    """
    Test get_inode returns None for missing path (edge case).
    """
    m = PathInodeMap()
    assert m.get_inode("/not/found") is None


def test_get_path_missing() -> None:
    """
    Test get_path returns None for missing inode (failure case).
    """
    m = PathInodeMap()
    assert m.get_path(999) is None
