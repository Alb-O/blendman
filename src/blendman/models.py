"""
Database models for files, directories, and rename logs.

Implements parent/child relationships and event log linkage.
All models are PEP8-compliant and use type hints.
"""

from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel  # type: ignore


class FileDirModel(BaseModel):
    """
    Represents a file or directory in the system.

    Args:
            id (str): Unique identifier.
            name (str): File or directory name.
            path (str): Absolute path.
            parent_id (Optional[str]): Parent file/dir id (None for root).
            type (Literal['file', 'dir']): Type of entry.
            created_at (datetime): Creation timestamp.
            updated_at (datetime): Last update timestamp.
    """

    id: str
    name: str
    path: str
    parent_id: Optional[str] = None
    type: Literal["file", "dir"]
    created_at: datetime
    updated_at: datetime


class RenameLogModel(BaseModel):
    """
    Represents a rename/move event for a file or directory.

    Args:
            id (str): Unique identifier.
            file_id (str): FK to FileDirModel.id.
            old_path (str): Previous path.
            new_path (str): New path after event.
            event_type (Literal['rename', 'move', 'create', 'delete']): Event type.
            timestamp (datetime): Event timestamp.
    """

    id: str
    file_id: str
    old_path: str
    new_path: str
    event_type: Literal["rename", "move", "create", "delete"]
    timestamp: datetime
