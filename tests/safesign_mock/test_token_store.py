"""Tests for safesign_mock.token_store.TokenStore."""

import threading
from safesign_mock import ObjectClass


class TestStore:
    def test_store_returns_integer_handle(self, token_store):
        h = token_store.store({"class": ObjectClass.DATA, "label": "x"})
        assert isinstance(h, int)

    def test_store_increments_handles(self, token_store):
        h1 = token_store.store({"label": "a"})
        h2 = token_store.store({"label": "b"})
        h3 = token_store.store({"label": "c"})
        assert h1 == 1 and h2 == 2 and h3 == 3

    def test_count_increases_on_store(self, token_store):
        assert token_store.count == 0
        token_store.store({"label": "a"})
        assert token_store.count == 1
        token_store.store({"label": "b"})
        assert token_store.count == 2


class TestGet:
    def test_get_returns_stored_object(self, token_store):
        obj = {"class": ObjectClass.PUBLIC_KEY, "label": "mykey"}
        h = token_store.store(obj)
        assert token_store.get(h) is obj

    def test_get_returns_none_for_missing_handle(self, token_store):
        assert token_store.get(999) is None


class TestFind:
    def test_find_by_single_attribute(self, token_store):
        token_store.store({"class": ObjectClass.PUBLIC_KEY, "label": "a"})
        token_store.store({"class": ObjectClass.PRIVATE_KEY, "label": "b"})
        results = token_store.find(**{"class": ObjectClass.PUBLIC_KEY})
        assert len(results) == 1
        assert results[0][1]["label"] == "a"

    def test_find_by_multiple_attributes(self, token_store):
        token_store.store({"class": ObjectClass.PUBLIC_KEY, "label": "x"})
        token_store.store({"class": ObjectClass.PUBLIC_KEY, "label": "y"})
        results = token_store.find(**{"class": ObjectClass.PUBLIC_KEY, "label": "x"})
        assert len(results) == 1

    def test_find_returns_empty_for_no_match(self, token_store):
        token_store.store({"label": "a"})
        assert token_store.find(label="nonexistent") == []

    def test_find_returns_handle_and_object_tuples(self, token_store):
        token_store.store({"label": "a"})
        results = token_store.find(label="a")
        assert len(results) == 1
        handle, obj = results[0]
        assert isinstance(handle, int)
        assert isinstance(obj, dict)


class TestDelete:
    def test_delete_existing_returns_true(self, token_store):
        h = token_store.store({"label": "a"})
        assert token_store.delete(h) is True

    def test_delete_nonexistent_returns_false(self, token_store):
        assert token_store.delete(999) is False

    def test_delete_removes_from_store(self, token_store):
        h = token_store.store({"label": "a"})
        token_store.delete(h)
        assert token_store.get(h) is None
        assert token_store.count == 0


class TestListAll:
    def test_list_all_empty_store(self, token_store):
        assert token_store.list_all() == []

    def test_list_all_returns_all_objects(self, token_store):
        token_store.store({"label": "a"})
        token_store.store({"label": "b"})
        assert len(token_store.list_all()) == 2


class TestThreadSafety:
    def test_concurrent_stores_produce_unique_handles(self, token_store):
        handles = []
        lock = threading.Lock()

        def store_one():
            h = token_store.store({"label": "t"})
            with lock:
                handles.append(h)

        threads = [threading.Thread(target=store_one) for _ in range(100)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(handles) == 100
        assert len(set(handles)) == 100  # all unique
        assert token_store.count == 100
