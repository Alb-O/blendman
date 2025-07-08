"""
Path-inode mapping utilities for rename_watcher.
"""

from typing import Dict, Optional


class PathInodeMap:
    """
    Maintains a two-way mapping between file paths and inodes (or platform equivalent).
    """

    def __init__(self) -> None:
        self.path_to_inode: Dict[str, int] = {}
        self.inode_to_path: Dict[int, str] = {}

    def add(self, path: str, inode: int) -> None:
        """
        Add a path-inode mapping.
        """
        self.path_to_inode[path] = inode
        self.inode_to_path[inode] = path

    def get_inode(self, path: str) -> Optional[int]:
        """
        Get inode for a given path.
        """
        return self.path_to_inode.get(path)

    def get_path(self, inode: int) -> Optional[str]:
        """
        Get path for a given inode.
        """
        return self.inode_to_path.get(inode)
