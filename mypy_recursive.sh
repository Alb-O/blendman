#!/bin/sh
# Robust mypy workflow for src-layout Python project (procedural)
set -e


RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

command -v uv >/dev/null 2>&1 || { echo "${RED}Error: 'uv' is not installed. Aborting.${NC}" >&2; exit 1; }
uv run mypy --version >/dev/null 2>&1 || { echo "${RED}Error: 'mypy' is not installed in uv environment. Aborting.${NC}" >&2; exit 1; }

printf "%b\n" "${YELLOW}Type checking main source code: $SRC_DIR ...${NC}"


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
  printf "%b\n" "${YELLOW}Type checking main source code: $SRC_DIR ...${NC}"
  if uv run mypy "$SRC_DIR"; then
    printf "%b\n" "${GREEN}Main source code: PASSED ($SRC_DIR)${NC}"
  else
    printf "%b\n" "${RED}Main source code: FAILED ($SRC_DIR)${NC}"
    exit 1
  fi

  # Find sibling tests/ dir for this src/*
  PKG_DIR=$(dirname "$SRC_DIR")
  TEST_DIR="$PKG_DIR/tests"
  if [ -d "$TEST_DIR" ]; then
    printf "%b\n" "${YELLOW}Type checking tests in $TEST_DIR with src in MYPYPATH...${NC}"
    if MYPYPATH="$PKG_DIR" uv run mypy "$TEST_DIR"; then
      printf "%b\n" "${GREEN}Tests in $TEST_DIR: PASSED${NC}"
    else
      printf "%b\n" "${RED}Tests in $TEST_DIR: FAILED${NC}"
      exit 1
    fi
  else
    printf "%b\n" "${YELLOW}No tests/ found for $SRC_DIR. Skipping test type checks for this package.${NC}"
  fi
done

printf "%b\n" "${GREEN}All mypy checks passed!${NC}"
