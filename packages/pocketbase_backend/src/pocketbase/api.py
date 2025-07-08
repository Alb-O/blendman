"""
Main API client for interacting with PocketBase REST API.
"""

# pylint: disable=too-few-public-methods
from .utils import load_env
from .auth import AuthClient
from .collections import CollectionsClient
from .files import FilesClient
from .relations import RelationsClient


class PocketBaseAPI:
    """
    Main entry point for PocketBase API operations.
    """

    def __init__(self):
        load_env()
        self.auth = AuthClient()
        self.collections = CollectionsClient()
        self.files = FilesClient()
        self.relations = RelationsClient()
