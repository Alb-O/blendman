"""
Unit tests for TokenManager (token management utilities).
"""

from pocketbase.tokens import TokenManager


def test_token_manager_set_and_get():
    tm = TokenManager()
    tm.set_token("abc")
    assert tm.get_token() == "abc"
    tm.clear_token()
    assert tm.get_token() is None


def test_token_manager_thread_safety():
    import threading

    tm = TokenManager()

    def set_token():
        tm.set_token("thread")

    threads = [threading.Thread(target=set_token) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert tm.get_token() == "thread"
