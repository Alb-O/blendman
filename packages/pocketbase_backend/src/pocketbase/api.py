"""
Main API client for interacting with PocketBase REST API.
"""


class PocketBaseAPI:
    """
    Main entry point for PocketBase API operations.
    """

    def __init__(self):
        # Import here for testability and monkeypatching
        from .utils import load_env
        from .auth import AuthClient
        from .collections import CollectionsClient
        from .files import FilesClient
        from .relations import RelationsClient

        load_env()
        self.auth = AuthClient()
        self.collections = CollectionsClient()
        self.files = FilesClient()
        self.relations = RelationsClient()
