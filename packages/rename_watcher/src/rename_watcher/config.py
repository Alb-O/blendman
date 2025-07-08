"""
Configuration and environment loading for rename_watcher.
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()


def get_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables.

    Returns:
        Dict[str, Any]: Configuration dictionary.
    """
    return {
        "timeout": float(os.getenv("WATCHER_TIMEOUT", 2.0)),
        "poll_interval": float(os.getenv("WATCHER_POLL_INTERVAL", 1.0)),
        "ignore_patterns": os.getenv("WATCHER_IGNORE_PATTERNS", ".git,.env").split(","),
    }
