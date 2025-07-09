#!/usr/bin/env python3
"""Unified development script for lint, type, and test.

This script replaces the previous dev.sh and dev.ps1 wrappers with a
single Python implementation that works on Linux, macOS and Windows.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
NC = "\033[0m"


def run_cmd(cmd: list[str], *, env: dict[str, str] | None = None) -> None:
    """Run a command, raising if it fails."""
    subprocess.run(cmd, check=True, env=env)


def ensure_uv_and_mypy() -> None:
    if shutil.which("uv") is None:
        print(f"{RED}Error: 'uv' is not installed. Aborting.{NC}", file=sys.stderr)
        sys.exit(1)
    try:
        subprocess.run(
            ["uv", "run", "mypy", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        print(
            f"{RED}Error: 'mypy' is not installed in uv environment. Aborting.{NC}",
            file=sys.stderr,
        )
        sys.exit(1)


def find_src_roots() -> list[Path]:
    roots: list[Path] = []
    for d in Path("packages").rglob("src"):
        for sub in d.rglob("*"):
            if sub.is_dir() and (sub / "__init__.py").exists():
                roots.append(sub)
    return roots


def parse_extra_paths() -> str:
    settings = Path(".vscode/settings.json")
    if not settings.exists():
        return ""
    try:
        data = json.loads(settings.read_text())
    except json.JSONDecodeError:
        print(f"{YELLOW}Warning: failed to parse {settings}{NC}")
        return ""
    paths = data.get("python.analysis.extraPaths", [])
    resolved = [str(Path(p).resolve()) for p in paths]
    return os.pathsep.join(resolved)


def run_pylint() -> None:
    py_files = (
        subprocess.run(
            ["git", "ls-files", "*.py"], check=True, text=True, capture_output=True
        ).stdout.splitlines()
        + subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "*.py"],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.splitlines()
    )
    if not py_files:
        print(f"{YELLOW}No Python files found for pylint.{NC}")
        return

    pythonpath = parse_extra_paths()
    env = os.environ.copy()
    if pythonpath:
        env["PYTHONPATH"] = pythonpath
        print(f"PYTHONPATH for pylint: {pythonpath}")
    else:
        print(
            f"{YELLOW}Warning: PYTHONPATH is empty. Pylint may not resolve imports correctly.{NC}"
        )

    try:
        run_cmd(
            ["uv", "run", "pylint", "-E", "--output-format=colorized", *py_files],
            env=env,
        )
        print(f"{GREEN}Pylint checks passed!{NC}")
    except subprocess.CalledProcessError:
        print(f"{RED}Pylint checks failed!{NC}")
        sys.exit(1)


def run_checks() -> None:
    run_cmd(["uv", "run", "ruff", "format", "."])
    run_cmd(["uv", "run", "ruff", "check", ".", "--fix"])
    run_cmd(["uv", "run", "ruff", "check", "."])

    src_roots = find_src_roots()
    if not src_roots:
        print(f"{RED}No src/* package roots with __init__.py found. Aborting.{NC}")
        sys.exit(1)

    for src_dir in src_roots:
        print(f"Type checking main source code: {src_dir} ...")
        run_cmd(["uv", "run", "mypy", str(src_dir)])

        pkg_root = src_dir.parent.parent
        test_dir = pkg_root / "tests"
        if test_dir.is_dir():
            env = os.environ.copy()
            env["MYPYPATH"] = f"{pkg_root / 'src'}{os.pathsep}{pkg_root}"
            print(f"Type checking tests in {test_dir} with src in MYPYPATH...")
            run_cmd(["uv", "run", "mypy", str(test_dir)], env=env)

    for src_dir in Path("packages").rglob("src"):
        pkg_dir = src_dir.parent
        test_dir = pkg_dir / "tests"
        if test_dir.is_dir():
            env = os.environ.copy()
            env["PYTHONPATH"] = str(src_dir)
            print(f"Running pytest for {test_dir} with PYTHONPATH={src_dir} ...")
            run_cmd(["uv", "run", "pytest", str(test_dir)], env=env)

    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        ["src", "packages/pocketbase_backend/src", "packages/rename_watcher/src"]
    )
    print(f"Running pytest for tests/blendman with PYTHONPATH={env['PYTHONPATH']} ...")
    run_cmd(["uv", "run", "pytest", "tests/blendman", "-v"], env=env)

    print(f"{GREEN}All mypy checks passed!{NC}")
    run_pylint()


def main() -> None:
    ensure_uv_and_mypy()
    if len(sys.argv) > 1 and sys.argv[1] == "--pylint":
        run_pylint()
    else:
        run_checks()


if __name__ == "__main__":
    main()
