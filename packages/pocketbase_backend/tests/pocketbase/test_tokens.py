"""
Unit tests for TokenManager (token management utilities).
"""

import threading
from pocketbase.tokens import TokenManager


def test_token_manager_set_and_get():
    """
    Test that set_token, get_token, and clear_token work as expected.
    """
    tm = TokenManager()
    tm.set_token("abc")
    assert tm.get_token() == "abc"
    tm.clear_token()
    assert tm.get_token() is None


def test_token_manager_thread_safety():
    """
    Test that TokenManager is thread-safe when setting tokens from multiple threads.
    """
    tm = TokenManager()

    def set_token():
        tm.set_token("thread")

    threads = [threading.Thread(target=set_token) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert tm.get_token() == "thread"
