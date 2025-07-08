"""
Main API client for interacting with PocketBase REST API.
"""

# pylint: disable=too-few-public-methods, import-outside-toplevel

from .utils import load_env


class PocketBaseAPI:
    """
    Main entry point for PocketBase API operations.
    """

    def __init__(self):
        from .auth import AuthClient
        from .collections import CollectionsClient
        from .files import FilesClient
        from .relations import RelationsClient

        load_env()
        self.auth = AuthClient()
        self.collections = CollectionsClient()
        self.files = FilesClient()
        self.relations = RelationsClient()
