"""Shared test data generators and helpers for rename_watcher fuzzing."""

# This module has helper functions with many parameters for flexibility
# pylint: disable=too-many-arguments,too-many-positional-arguments

import os
import random
import string
import threading
from typing import Callable, List, Optional


def random_filename(length: int = 12, edge_case: bool = False) -> str:
    """
    Generate a random filename, optionally with edge-case characters.

    Args:
        length (int): Length of the filename.
        edge_case (bool): If True, include unicode, reserved, and control chars.

    Returns:
        str: Random filename.
    """
    base = string.ascii_letters + string.digits
    if edge_case:
        # Add unicode, reserved, and control characters
        base += "_-. \u202e\u202d"
        base += "".join(chr(i) for i in range(0x20, 0x7F) if chr(i) not in "/\\")
        base += "".join(chr(i) for i in range(1, 32) if i != 0 and chr(i) not in "/\\")
    return "".join(random.choice(base) for _ in range(length))


def random_file_tree(
    root: str,
    depth: int = 3,
    breadth: int = 3,
    files_per_dir: int = 3,
    edge_case_names: bool = False,
    create_file: Optional[Callable[[str], None]] = None,
    create_dir: Optional[Callable[[str], None]] = None,
) -> List[str]:
    """
    Recursively generate a random file/directory tree.

    Args:
        root (str): Root directory path.
        depth (int): Max depth of tree.
        breadth (int): Max subdirectories per directory.
        files_per_dir (int): Files per directory.
        edge_case_names (bool): Use edge-case filenames.
        create_file (Callable): Function to create a file at a path.
        create_dir (Callable): Function to create a directory at a path.

    Returns:
        List[str]: List of all file paths created.
    """
    files: List[str] = []
    if create_dir:
        create_dir(root)
    for _ in range(files_per_dir):
        fname = random_filename(16 if edge_case_names else 8, edge_case=edge_case_names)
        fpath = os.path.join(root, fname)
        if create_file:
            create_file(fpath)
        files.append(fpath)
    if depth > 0:
        for _ in range(breadth):
            dname = random_filename(
                10 if edge_case_names else 5, edge_case=edge_case_names
            )
            dpath = os.path.join(root, dname)
            files.extend(
                random_file_tree(
                    dpath,
                    depth - 1,
                    breadth,
                    files_per_dir,
                    edge_case_names,
                    create_file,
                    create_dir,
                )
            )
    return files


def run_concurrent_ops(ops: List[Callable[[], None]], max_threads: int = 4) -> None:
    """
    Run a list of operations concurrently (threaded).
    Note: pyfakefs is not fully thread-safe; use with caution.

    Args:
        ops (List[Callable[[], None]]): List of operations to run.
        max_threads (int): Max number of concurrent threads.
    """
    threads: List[threading.Thread] = []
    for op in ops:
        t: threading.Thread = threading.Thread(target=op)
        threads.append(t)
        t.start()
        if len(threads) >= max_threads:
            for th in threads:
                th.join()
            threads = []
    for th in threads:
        th.join()
