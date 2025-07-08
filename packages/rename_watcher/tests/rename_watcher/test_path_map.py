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


def test_descendants_simple() -> None:
    """
    Test descendants returns all nested files/folders (expected use).
    """
    m = PathInodeMap()
    m.add("/root/a.txt", 1)
    m.add("/root/folder/b.txt", 2)
    m.add("/root/folder/sub/c.txt", 3)
    m.add("/root2/d.txt", 4)
    result = m.descendants("/root")
    assert "/root/a.txt" in result
    assert "/root/folder/b.txt" in result
    assert "/root/folder/sub/c.txt" in result
    assert "/root2/d.txt" not in result


def test_bulk_update_paths_simple() -> None:
    """
    Test bulk_update_paths updates all descendants on folder move (expected use).
    """
    m = PathInodeMap()
    m.add("/root/a.txt", 1)
    m.add("/root/folder/b.txt", 2)
    m.add("/root/folder/sub/c.txt", 3)
    m.bulk_update_paths("/root/folder", "/root/renamed")
    assert m.get_inode("/root/renamed/b.txt") == 2
    assert m.get_inode("/root/renamed/sub/c.txt") == 3
    assert m.get_inode("/root/folder/b.txt") is None


def test_bulk_update_paths_edge_empty() -> None:
    """
    Test bulk_update_paths on folder with no descendants (edge case).
    """
    m = PathInodeMap()
    m.add("/root/a.txt", 1)
    m.bulk_update_paths("/root/empty", "/root/other")  # Should not error
    assert m.get_inode("/root/a.txt") == 1


def test_bulk_update_paths_nested() -> None:
    """
    Test bulk_update_paths on deeply nested structure (edge case).
    """
    m = PathInodeMap()
    m.add("/a/b/c/d.txt", 10)
    m.bulk_update_paths("/a/b", "/a/x")
    assert m.get_inode("/a/x/c/d.txt") == 10
    assert m.get_inode("/a/b/c/d.txt") is None
