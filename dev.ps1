# Requires -Version 7.0
param(
    [string]$Mode = ""
)

# Color definitions
$RED = "`e[0;31m"
$GREEN = "`e[0;32m"
$YELLOW = "`e[1;33m"
$NC = "`e[0m"

function Write-Color($Color, $Message) {
    Write-Host "$Color$Message$NC"
}

function Abort($Message) {
    Write-Color $RED $Message
    exit 1
}

# Check for uv
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Abort "Error: 'uv' is not installed. Aborting."
}

# Check for mypy in uv
try {
    uv run mypy --version | Out-Null
} catch {
    Abort "Error: 'mypy' is not installed in uv environment. Aborting."
}

if ($Mode -eq "--pylint") {
    Write-Color $YELLOW "Running pylint only (--pylint mode)..."
    if (-not (Get-Command jq -ErrorAction SilentlyContinue)) {
        Abort "Error: 'jq' is required to parse .vscode/settings.json. Aborting.\nInstall it with: winget install jqlang.jq"
    }
    $EXTRA_PATHS = & jq -r '".python.analysis.extraPaths"[]?' .vscode/settings.json 2>$null | ForEach-Object { $_.Trim() }
    $PYTHONPATH = ($EXTRA_PATHS | ForEach-Object { $(Resolve-Path $_).Path }) -join ";"
    $PY_FILES = @()
    $PY_FILES += & git ls-files '*.py'
    $PY_FILES += & git ls-files --others --exclude-standard '*.py'
    if (-not $PY_FILES) {
        Write-Color $YELLOW "No Python files found for pylint."
    } else {
        Write-Color $YELLOW "PYTHONPATH for pylint: $PYTHONPATH"
        $env:PYTHONPATH = $PYTHONPATH
        if (uv run pylint --output-format=colorized $PY_FILES) {
            Write-Color $GREEN "Pylint checks passed!"
        } else {
            Abort "Pylint checks failed!"
        }
    }
    exit 0
}

# Format and lint
uv run ruff format .
uv run ruff check . --fix
uv run ruff check .

# Find all src/* package roots (e.g. packages/*/src/*) that contain __init__.py
$SRC_ROOTS = Get-ChildItem -Recurse -Directory -Path ./packages | Where-Object { $_.FullName -match "\\src\\" -and (Test-Path (Join-Path $_.FullName '__init__.py')) } | ForEach-Object { $_.FullName }
if (-not $SRC_ROOTS) {
    Abort "No src/* package roots with __init__.py found. Aborting."
}

foreach ($SRC_DIR in $SRC_ROOTS) {
    Write-Color $NC "Type checking main source code: $SRC_DIR ..."
    if (uv run mypy $SRC_DIR) {
        Write-Color $GREEN "Main source code: PASSED ($SRC_DIR)"
    } else {
        Abort "Main source code: FAILED ($SRC_DIR)"
    }
    $PKG_ROOT = Split-Path (Split-Path $SRC_DIR -Parent) -Parent
    $TEST_DIR = Join-Path $PKG_ROOT 'tests'
    if (Test-Path $TEST_DIR) {
        Write-Color $NC "Type checking tests in $TEST_DIR with src in MYPYPATH..."
    $env:MYPYPATH = "$PKG_ROOT/src;$PKG_ROOT"
        if (uv run mypy $TEST_DIR) {
            Write-Color $GREEN "Tests in ${TEST_DIR}: PASSED"
        } else {
            Abort "Tests in ${TEST_DIR}: FAILED"
        }
    }
}

# Dynamically discover all package src/tests pairs and run pytest with correct PYTHONPATH
$SRC_DIRS = Get-ChildItem -Recurse -Directory -Path ./packages | Where-Object { $_.FullName -like '*\src' }
foreach ($SRC in $SRC_DIRS) {
    $PKG_DIR = Split-Path $SRC.FullName -Parent
    $TEST_DIR = Join-Path $PKG_DIR 'tests'
    if (Test-Path $TEST_DIR) {
        Write-Color $NC "Running pytest for $TEST_DIR with PYTHONPATH=$($SRC.FullName) ..."
        $env:PYTHONPATH = $SRC.FullName
        uv run pytest $TEST_DIR
    }
}

Write-Color $GREEN "All mypy checks passed!"

# --- Pylint section: use python.analysis.extraPaths for PYTHONPATH ---
Write-Color $YELLOW "Running pylint with VSCode extraPaths..."
if (-not (Get-Command jq -ErrorAction SilentlyContinue)) {
    Abort "Error: 'jq' is required to parse .vscode/settings.json. Aborting.\nInstall it with: winget install jqlang.jq"
}
$EXTRA_PATHS = & jq -r '".python.analysis.extraPaths"[]?' .vscode/settings.json 2>$null | ForEach-Object { $_.Trim() }
$PYTHONPATH = ($EXTRA_PATHS | ForEach-Object { $(Resolve-Path $_).Path }) -join ";"
$PY_FILES = @()
$PY_FILES += & git ls-files '*.py'
$PY_FILES += & git ls-files --others --exclude-standard '*.py'
if (-not $PY_FILES) {
    Write-Color $YELLOW "No Python files found for pylint."
} else {
    Write-Color $YELLOW "PYTHONPATH for pylint: $PYTHONPATH"
    $env:PYTHONPATH = $PYTHONPATH
    if (uv run pylint --output-format=colorized $PY_FILES) {
        Write-Color $GREEN "Pylint checks passed!"
    } else {
        Abort "Pylint checks failed!"
    }
}
