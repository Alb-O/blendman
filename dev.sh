#!/usr/bin/env bash
set -euo pipefail

uv run ruff format .
uv run ruff check . --fix
uv run ruff check .

set -e

RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

command -v uv >/dev/null 2>&1 || { echo "${RED}Error: 'uv' is not installed. Aborting.${NC}" >&2; exit 1; }
uv run mypy --version >/dev/null 2>&1 || { echo "${RED}Error: 'mypy' is not installed in uv environment. Aborting.${NC}" >&2; exit 1; }

if [ "${1-}" = "--pylint" ]; then
  YELLOW="\033[1;33m"
  GREEN="\033[0;32m"
  RED="\033[0;31m"
  NC="\033[0m"
  printf "%b\n" "${YELLOW}Running pylint only (--pylint mode)...${NC}"
  # Extract extraPaths from .vscode/settings.json (assumes jq is installed)
  if ! command -v jq >/dev/null 2>&1; then
    printf "%b\n" "${RED}Error: 'jq' is required to parse .vscode/settings.json. Aborting.${NC}"
    exit 1
  fi

  EXTRA_PATHS=$(jq -r '."python.analysis.extraPaths"[]?' .vscode/settings.json 2>/dev/null | xargs)
  PYTHONPATH=""
  for p in $EXTRA_PATHS; do
    PYTHONPATH="$PYTHONPATH:$(realpath "$p")"
  done
  PYTHONPATH=${PYTHONPATH#:} # Remove leading colon

  if [ -z "$PYTHONPATH" ]; then
    printf "%b\n" "${YELLOW}Warning: PYTHONPATH is empty. Pylint may not resolve imports correctly. Check .vscode/settings.json or dev.sh logic.${NC}"
  fi

  PY_FILES=$(git ls-files '*.py'; git ls-files --others --exclude-standard '*.py')

  if [ -z "$PY_FILES" ]; then
    printf "%b\n" "${YELLOW}No Python files found for pylint.${NC}"
  else
    printf "%b\n" "${YELLOW}PYTHONPATH for pylint: $PYTHONPATH${NC}"
    if PYTHONPATH="$PYTHONPATH" uv run pylint --output-format=colorized $PY_FILES; then
      printf "%b\n" "${GREEN}Pylint checks passed!${NC}"
    else
      printf "%b\n" "${RED}Pylint checks failed!${NC}"
      exit 1
    fi
  fi
  exit 0
fi

# Find all src/* package roots (e.g. packages/*/src/*) that contain __init__.py
SRC_ROOTS=""
while IFS= read -r dir; do
  if [ -f "$dir/__init__.py" ]; then
    SRC_ROOTS="$SRC_ROOTS $dir"
  fi
done < <(find ./packages -type d -path "*/src/*" \
  | grep -v "/\\." \
  | grep -v ".mypy_cache" \
  | grep -v "__pycache__" \
  | grep -v "/\.[^/]*$")
SRC_ROOTS=$(echo $SRC_ROOTS)
if [ -z "$SRC_ROOTS" ]; then
  printf "%b\n" "${RED}No src/* package roots with __init__.py found. Aborting.${NC}"
  exit 1
fi

for SRC_DIR in $SRC_ROOTS; do
  printf "%b\n" "${NC}Type checking main source code: $SRC_DIR ...${NC}"
  if uv run mypy "$SRC_DIR"; then
    printf "%b\n" "${GREEN}Main source code: PASSED ($SRC_DIR)${NC}"
  else
    printf "%b\n" "${RED}Main source code: FAILED ($SRC_DIR)${NC}"
    exit 1
  fi

  # Find package root (parent of src/) and check for tests/ dir there
  PKG_ROOT=$(dirname $(dirname "$SRC_DIR"))
  TEST_DIR="$PKG_ROOT/tests"
  if [ -d "$TEST_DIR" ]; then
    printf "%b\n" "${NC}Type checking tests in $TEST_DIR with src in MYPYPATH...${NC}"
    if MYPYPATH="$PKG_ROOT/src:$PKG_ROOT" uv run mypy "$TEST_DIR"; then
      printf "%b\n" "${GREEN}Tests in $TEST_DIR: PASSED${NC}"
    else
      printf "%b\n" "${RED}Tests in $TEST_DIR: FAILED${NC}"
      exit 1
    fi
  fi
done

# Dynamically discover all package src/tests pairs and run pytest with correct PYTHONPATH
for SRC_DIR in $(find ./packages -type d -path "*/src" | grep -v "/\\." | grep -v ".mypy_cache" | grep -v "__pycache__" | grep -v "/\.[^/]*$"); do
  PKG_DIR=$(dirname "$SRC_DIR")
  TEST_DIR="$PKG_DIR/tests"
  if [ -d "$TEST_DIR" ]; then
    printf "%b\n" "${NC}Running pytest for $TEST_DIR with PYTHONPATH=$SRC_DIR ...${NC}"
    PYTHONPATH="$SRC_DIR" uv run pytest "$TEST_DIR"
  fi
done


# Always run blendman tests with full PYTHONPATH
printf "%b\n" "${NC}Running pytest for tests/blendman with PYTHONPATH=src:packages/pocketbase_backend/src:packages/rename_watcher/src ...${NC}"
PYTHONPATH="src:packages/pocketbase_backend/src:packages/rename_watcher/src" uv run pytest tests/blendman -v

printf "%b\n" "${GREEN}All mypy checks passed!${NC}"

# --- Pylint section: use python.analysis.extraPaths for PYTHONPATH ---
printf "%b\n" "${NC}Running pylint with VSCode extraPaths...${NC}"

# Extract extraPaths from .vscode/settings.json (assumes jq is installed)
if ! command -v jq >/dev/null 2>&1; then
  printf "%b\n" "${RED}Error: 'jq' is required to parse .vscode/settings.json. Aborting.${NC}"
  exit 1
fi

EXTRA_PATHS=$(jq -r '."python.analysis.extraPaths"[]?' .vscode/settings.json 2>/dev/null | xargs)
PYTHONPATH=""
for p in $EXTRA_PATHS; do
  PYTHONPATH="$PYTHONPATH:$(realpath "$p")"
done
PYTHONPATH=${PYTHONPATH#:} # Remove leading colon

# Find all Python files tracked by git (including untracked, not ignored)
PY_FILES=$(git ls-files '*.py'; git ls-files --others --exclude-standard '*.py')

if [ -z "$PY_FILES" ]; then
  printf "%b\n" "${YELLOW}No Python files found for pylint.${NC}"
else
  if [ -z "$PYTHONPATH" ]; then
    printf "%b\n" "${YELLOW}Warning: PYTHONPATH is empty. Pylint may not resolve imports correctly. Check .vscode/settings.json or dev.sh logic.${NC}"
  else
    printf "%b\n" "${NC}PYTHONPATH for pylint: $PYTHONPATH${NC}"
  fi
  if PYTHONPATH="$PYTHONPATH" uv run pylint --output-format=colorized $PY_FILES; then
    printf "%b\n" "${GREEN}Pylint checks passed!${NC}"
  else
    printf "%b\n" "${RED}Pylint checks failed!${NC}"
    exit 1
  fi
fi
