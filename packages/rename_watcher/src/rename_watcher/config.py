"""
Configuration and environment loading for rename_watcher.
"""

import os
import pathlib
from dotenv import load_dotenv
from typing import Dict, Any, Callable, List

load_dotenv()

try:
    import tomli
except ImportError:
    tomli = None  # type: ignore[assignment]

try:
    import pathspec
except ImportError:
    pathspec = None  # type: ignore[assignment]


def get_toml_config() -> Dict[str, Any]:
    """
    Load configuration from a TOML file if it exists. Uses WATCHER_CONFIG_TOML env var if set.

    Returns:
        Dict[str, Any]: Configuration dictionary, or empty dict if not found or invalid.
    """
    if not tomli:
        raise ImportError("tomli is required for TOML config parsing.")
    config_path = os.getenv("WATCHER_CONFIG_TOML", "watcher_config.toml")
    if not os.path.exists(config_path):
        return {}
    try:
        with open(config_path, "rb") as f:
            return tomli.load(f)
    except Exception:
        # Fallback to empty config if TOML is invalid
        return {}


def get_patterns_from_config(config: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Extract include and ignore patterns from config dict.

    Args:
        config (Dict[str, Any]): Config dict from TOML or env.

    Returns:
        Dict[str, List[str]]: Dict with 'include' and 'ignore' pattern lists.
    """
    include = []
    ignore = []
    if "include" in config and isinstance(config["include"], dict):
        include = config["include"].get("patterns", [])  # type: ignore[attr-defined]
    if "ignore" in config and isinstance(config["ignore"], dict):
        ignore = config["ignore"].get("patterns", [])  # type: ignore[attr-defined]
    return {"include": include, "ignore": ignore}


def get_env_patterns() -> Dict[str, List[str]]:
    """
    Fallback: Get ignore patterns from environment variables.

    Returns:
        Dict[str, List[str]]: Dict with 'include' and 'ignore' pattern lists.
    """
    ignore = os.getenv("WATCHER_IGNORE_PATTERNS", ".git,.env").split(",")
    include = (
        os.getenv("WATCHER_INCLUDE_PATTERNS", "").split(",")
        if os.getenv("WATCHER_INCLUDE_PATTERNS")
        else []
    )
    return {"include": include, "ignore": ignore}


def get_path_matcher(patterns: Dict[str, List[str]]) -> Callable[[str], bool]:
    """
    Return a matcher function that returns True if a path should be included (not ignored),
    supporting gitignore negation in include patterns.

    Args:
        patterns (Dict[str, List[str]]): Dict with 'include' and 'ignore' pattern lists.

    Returns:
        Callable[[str], bool]: Matcher function.
    """
    if not pathspec:
        raise ImportError("pathspec is required for gitignore-style pattern matching.")

    def preprocess(pat: str) -> str:
        """
        Convert bare extensions (e.g., '.blend') to '*.blend' for pathspec compatibility.
        Handles negation (!.blend -> !*.blend).
        """
        if pat.startswith("!"):
            core = pat[1:]
            if core.startswith(".") and all(c not in core for c in "/*?[]!\\"):
                return "!*" + core
            return pat
        if pat.startswith(".") and all(c not in pat for c in "/*?[]!\\"):
            return "*" + pat
        return pat

    ignore_patterns = [preprocess(p) for p in patterns["ignore"]]
    include_patterns = [preprocess(p) for p in patterns["include"]]
    ignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", ignore_patterns)
    # Split include patterns into positive and negative (negated with '!')
    positive_patterns = [p for p in include_patterns if not p.startswith("!")]
    negative_patterns = [p[1:] for p in include_patterns if p.startswith("!")]
    include_spec = pathspec.PathSpec.from_lines("gitwildmatch", positive_patterns)
    exclude_spec = pathspec.PathSpec.from_lines("gitwildmatch", negative_patterns)

    def matcher(path: str) -> bool:
        rel_path = pathlib.PurePath(path).as_posix()
        if ignore_spec.match_file(rel_path):
            return False
        if include_patterns:
            if include_spec.match_file(rel_path):
                if exclude_spec.match_file(rel_path):
                    return False
                return True
            return False
        return True  # If no include patterns, include all not ignored

    return matcher


def get_config() -> Dict[str, Any]:
    """
    Load configuration from TOML file if present, else from environment variables.

    Returns:
        Dict[str, Any]: Configuration dictionary.
    """
    config = get_toml_config()
    if config:
        patterns = get_patterns_from_config(config)
    else:
        patterns = get_env_patterns()
    return {
        "timeout": float(os.getenv("WATCHER_TIMEOUT", 2.0)),
        "poll_interval": float(os.getenv("WATCHER_POLL_INTERVAL", 1.0)),
        "patterns": patterns,
        "matcher": get_path_matcher(patterns),
    }
