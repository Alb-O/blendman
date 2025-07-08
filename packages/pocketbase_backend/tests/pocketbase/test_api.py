"""
Tests for api.py (PocketBaseAPI composition and env loading).
"""

import sys  # type: ignore
import os  # type: ignore
import pytest
from _pytest.monkeypatch import MonkeyPatch
from pocketbase.api import PocketBaseAPI  # type: ignore

# sys.path modification is required for local import resolution in test runner environments.
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
)  # type: ignore


def test_api_composes_subclients():
    """
    Expected: PocketBaseAPI composes all subclients and loads env.
    """
    api = PocketBaseAPI()  # type: ignore
    assert hasattr(api, "auth")  # type: ignore
    assert hasattr(api, "collections")  # type: ignore
    assert hasattr(api, "files")  # type: ignore
    assert hasattr(api, "relations")  # type: ignore


def test_api_env_loaded(monkeypatch: MonkeyPatch):
    """
    Edge: load_env is called on init (simulate with monkeypatch).
    """
    called = {}

    def fake_load_env():
        called["env"] = True

    monkeypatch.setattr(
        "pocketbase.api.load_env", fake_load_env
    )  # Patch the correct reference
    PocketBaseAPI()
    assert called["env"]


def test_api_invalid_import(monkeypatch: MonkeyPatch):
    """
    Failure: If a subclient import fails, raise ImportError.
    """
    monkeypatch.setattr(
        "pocketbase.auth.AuthClient", lambda: (_ for _ in ()).throw(ImportError("fail"))
    )  # type: ignore
    with pytest.raises(ImportError):
        PocketBaseAPI()
