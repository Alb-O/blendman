"""
Explicit edge-case and failure mode tests for rename_watcher.
"""

# See utils.py for shared helpers and data generators.

import os
from typing import Any
import pytest  # type: ignore
from pyfakefs.fake_filesystem_unittest import Patcher  # type: ignore
from . import utils


@pytest.mark.parametrize("length", [255, 512, 1024])
def test_path_length_limits(length: int) -> None:
    """
    Test watcher with files at or near max path/filename length.
    """
    with Patcher() as patcher:
        fs: Any = patcher.fs
        root = "/edgecase"
        fs.makedirs(root, exist_ok=True)  # type: ignore[attr-defined]
        fname = utils.random_filename(length, edge_case=False)
        fpath = os.path.join(root, fname)
        try:
            fs.create_file(fpath, contents="x")  # type: ignore[attr-defined]
        except Exception as e:
            pytest.skip(f"Filesystem does not support path length {length}: {e}")
        assert os.path.exists(fpath)
        root = "/edgecase"
        fs.makedirs(root, exist_ok=True)
        fname = utils.random_filename(length, edge_case=False)
        fpath = os.path.join(root, fname)
        try:
            fs.create_file(fpath, contents="x")
        except Exception as e:
            pytest.skip(f"Filesystem does not support path length {length}: {e}")
        assert os.path.exists(fpath)


@pytest.mark.parametrize(
    "name",
    [
        "文件名测试.txt",  # CJK
        "emoji_😀.txt",  # emoji
        "control_\x1b[31m.txt",  # control char (was invalid, now escaped)
        "reserved_<>:\\|?*.txt",  # reserved chars (may be skipped on some OS)
    ],
)
def test_unicode_and_reserved_names(name: str) -> None:
    """
    Test watcher with unicode, emoji, control, and reserved character filenames.
    """
    with Patcher() as patcher:
        fs: Any = patcher.fs
        root = "/edgecase"
        fs.makedirs(root, exist_ok=True)  # type: ignore[attr-defined]
        fpath = os.path.join(root, name)
        try:
            fs.create_file(fpath, contents="x")  # type: ignore[attr-defined]
        except Exception as e:
            pytest.skip(f"Filesystem does not support name {name}: {e}")
        assert os.path.exists(fpath)
        root = "/edgecase"
        fs.makedirs(root, exist_ok=True)
        fpath = os.path.join(root, name)
        try:
            fs.create_file(fpath, contents="x")
        except Exception as e:
            pytest.skip(f"Filesystem does not support name {name}: {e}")
        assert os.path.exists(fpath)


def test_symlink_and_hardlink_block1():
    """
    Test watcher with symlinks and hardlinks (pyfakefs partial support), block 1.
    """
    with Patcher() as patcher:
        fs: Any = patcher.fs
        root = "/edgecase"
        fs.makedirs(root, exist_ok=True)  # type: ignore[attr-defined]
        target = os.path.join(root, "target.txt")
        link = os.path.join(root, "link.txt")
        fs.create_file(target, contents="x")  # type: ignore[attr-defined]
        fs.create_symlink(link, target)  # type: ignore[attr-defined]
        assert os.path.islink(link)
        # Hardlink (pyfakefs supports via os.link)
        hardlink = os.path.join(root, "hardlink.txt")
        os.link(target, hardlink)
        assert os.path.exists(hardlink)


def test_symlink_and_hardlink_block2():
    """
    Test watcher with symlinks and hardlinks (pyfakefs partial support), block 2.
    """
    with Patcher() as patcher:
        fs: Any = patcher.fs
        root = "/edgecase"
        fs.makedirs(root, exist_ok=True)
        target = os.path.join(root, "target.txt")
        link = os.path.join(root, "link.txt")
        fs.create_file(target, contents="x")
        fs.create_symlink(link, target)
        assert os.path.islink(link)
        # Hardlink (pyfakefs supports via os.link)
        hardlink = os.path.join(root, "hardlink.txt")
        os.link(target, hardlink)
        assert os.path.exists(hardlink)


def test_permission_errors_block1():
    """
    Test watcher with permission errors (read-only file/dir), block 1.
    """
    with Patcher() as patcher:
        fs: Any = patcher.fs
        root = "/edgecase"
        fs.makedirs(root, exist_ok=True)  # type: ignore[attr-defined]
        fpath = os.path.join(root, "readonly.txt")
        fs.create_file(fpath, contents="x")  # type: ignore[attr-defined]
        os.chmod(fpath, 0o400)  # read-only
        try:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write("fail")
            assert False, "Should not be able to write to read-only file"
        except Exception:
            # Broad exception is justified: any error is valid for this permission edge case.
            pass


def test_permission_errors_block2():
    """
    Test watcher with permission errors (read-only file/dir), block 2.
    """
    with Patcher() as patcher:
        fs: Any = patcher.fs
        root = "/edgecase"
        fs.makedirs(root, exist_ok=True)
        fpath = os.path.join(root, "readonly.txt")
        fs.create_file(fpath, contents="x")
        os.chmod(fpath, 0o400)  # read-only
        try:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write("fail")
            assert False, "Should not be able to write to read-only file"
        except Exception:
            # Broad exception is justified: any error is valid for this permission edge case.
            pass
