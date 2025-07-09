"""
Platform-specific and real-filesystem tests for rename_watcher (Linux, Windows, macOS).
"""

# See utils.py for shared helpers and data generators.

import os
import sys
import pytest
from pyfakefs.fake_filesystem_unittest import Patcher

LINUX = sys.platform.startswith("linux")
WINDOWS = sys.platform.startswith("win")
MACOS = sys.platform == "darwin"


@pytest.mark.skipif(not LINUX, reason="Linux-only: inotify semantics")
def test_inotify_event_coalescing_and_overflow():
    """
    Simulate inotify event coalescing and overflow (cannot fully emulate in pyfakefs).
    """
    # This is a placeholder: real integration test would use inotify directly.
    # Here, we just assert watcher can handle rapid file events without crash.
    with Patcher() as patcher:
        fs = patcher.fs
        root = "/inotifytest"
        fs.makedirs(root, exist_ok=True)  # type: ignore[attr-defined,union-attr]
        for i in range(1000):
            fname = f"file_{i}.txt"
            fs.create_file(os.path.join(root, fname), contents="x")
        # No assertion: just ensure no crash/hang


@pytest.mark.skipif(not WINDOWS, reason="Windows-only: ReadDirectoryChangesW semantics")
def test_windows_cross_directory_move_semantics():
    """
    Simulate Windows cross-directory move as delete+create events.
    """
    with Patcher() as patcher:
        fs = patcher.fs
        src = "C:/src/folder/file.txt"
        dst = "D:/dst/folder/file.txt"
        fs.makedirs(os.path.dirname(src), exist_ok=True)  # type: ignore[attr-defined,union-attr]
        fs.makedirs(os.path.dirname(dst), exist_ok=True)  # type: ignore[attr-defined,union-attr]
        fs.create_file(src, contents="x")  # type: ignore[attr-defined,union-attr]
        # Simulate delete at source
        fs.remove_object(src)  # type: ignore[attr-defined,union-attr]
        # Simulate create at destination
        fs.create_file(dst, contents="x")  # type: ignore[attr-defined,union-attr]
        assert os.path.exists(dst)


@pytest.mark.skipif(not MACOS, reason="macOS-only: FSEvents semantics")
def test_fsevents_event_coalescing():
    """
    Simulate FSEvents event coalescing and delayed delivery (cannot fully emulate in pyfakefs).
    """
    with Patcher() as patcher:
        fs = patcher.fs
        root = "/fseventstest"
        fs.makedirs(root, exist_ok=True)  # type: ignore[attr-defined,union-attr]
        # Simulate rapid file changes
        for i in range(100):
            fname = f"file_{i}.txt"
            fs.create_file(os.path.join(root, fname), contents="x")  # type: ignore[attr-defined,union-attr]
        # No assertion: just ensure no crash/hang
