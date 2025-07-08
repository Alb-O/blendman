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

    def descendants(self, folder_path: str) -> Dict[str, int]:
        """
        Return all descendants (paths and inodes) under a given folder path.

        Args:
            folder_path (str): The folder path to search under.

        Returns:
            Dict[str, int]: Mapping of descendant paths to inodes.
        """
        folder_path = folder_path.rstrip("/")
        result: Dict[str, int] = {}
        for path, inode in self.path_to_inode.items():
            if path.startswith(folder_path + "/"):
                result[path] = inode
        return result

    def bulk_update_paths(self, old_folder: str, new_folder: str) -> None:
        """
        Update all descendant paths when a folder is moved/renamed.

        Args:
            old_folder (str): The original folder path.
            new_folder (str): The new folder path.
        """
        old_folder = old_folder.rstrip("/")
        new_folder = new_folder.rstrip("/")
        updates: Dict[str, str] = {}
        # Update the folder itself
        if old_folder in self.path_to_inode:
            updates[old_folder] = new_folder
        # Update all descendants
        for path, _ in list(self.path_to_inode.items()):
            if path.startswith(old_folder + "/"):
                rel: str = path[len(old_folder) :]
                new_path: str = new_folder + rel
                updates[path] = new_path
        for old_path, new_path in updates.items():
            inode_val: int = self.path_to_inode.pop(old_path)
            self.path_to_inode[new_path] = inode_val
            self.inode_to_path[inode_val] = new_path

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
