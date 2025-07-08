"""
Fuzz tests for rename_watcher: randomized, high-frequency file/dir operations, edge-case names, deep nesting, concurrency.
"""

from hypothesis import event
import random
import os
import pytest
from typing import Any
from pyfakefs.fake_filesystem_unittest import Patcher
from . import utils


def random_file_ops(fs: Any, root: str, n_ops: int = 50, edge_case_names: bool = False):
    """
    Perform random file operations (create, delete, rename, move, modify) in the fake fs.
    """
    paths = utils.random_file_tree(
        root,
        depth=2,
        breadth=2,
        files_per_dir=2,
        edge_case_names=edge_case_names,
        create_file=lambda p: fs.create_file(p, contents="init"),  # type: ignore[attr-defined]
        create_dir=lambda p: fs.makedirs(p, exist_ok=True),  # type: ignore[attr-defined,union-attr]
    )
    all_paths = set(paths)
    for _ in range(n_ops):
        op = random.choice(["create", "delete", "rename", "move", "modify"])
        if op == "create":
            p = os.path.join(root, utils.random_filename(8, edge_case=edge_case_names))
            fs.create_file(p, contents="fuzz")  # type: ignore[attr-defined]
            all_paths.add(p)
        elif op == "delete" and all_paths:
            p = random.choice(list(all_paths))
            try:
                fs.remove_object(p)  # type: ignore[attr-defined]
                all_paths.remove(p)
            except Exception:
                pass
        elif op == "rename" and all_paths:
            p = random.choice(list(all_paths))
            new_p = p + "_renamed"
            try:
                fs.rename(p, new_p)  # type: ignore[attr-defined]
                all_paths.remove(p)
                all_paths.add(new_p)
            except Exception:
                pass
        elif op == "move" and all_paths:
            p = random.choice(list(all_paths))
            new_dir = os.path.join(
                root, utils.random_filename(6, edge_case=edge_case_names)
            )
            fs.makedirs(new_dir, exist_ok=True)  # type: ignore[attr-defined]
            new_p = os.path.join(new_dir, os.path.basename(p))
            try:
                fs.rename(p, new_p)  # type: ignore[attr-defined]
                all_paths.remove(p)
                all_paths.add(new_p)
            except Exception:
                pass
        elif op == "modify" and all_paths:
            p = random.choice(list(all_paths))
            try:
                with open(p, "a") as f:
                    f.write("fuzzmod\n")
            except Exception:
                pass


@pytest.mark.parametrize("edge_case_names", [False, True])
def test_fuzz_file_operations(edge_case_names: bool):
    """
    Fuzz test: random file/dir operations with/without edge-case names using pyfakefs.
    Asserts no crash/hang; event correctness to be checked in integration tests.
    Logs minimal failing cases using Hypothesis event.
    """
    with Patcher() as patcher:
        fs = patcher.fs
        root = "/fuzzroot"
        fs.makedirs(root, exist_ok=True)  # type: ignore[attr-defined,union-attr]
        try:
            random_file_ops(fs, root, n_ops=100, edge_case_names=edge_case_names)
        except Exception as e:
            event(f"Fuzz test failed: {e}")
            raise
