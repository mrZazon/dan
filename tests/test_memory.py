import json
import time

import pytest

from dan.memory.memory import MemoryManager


class TestMemoryManager:
    @pytest.fixture
    def tmp_memory(self, tmp_path):
        return MemoryManager(storage_path=tmp_path / "test_memory.json")

    def test_get_returns_none_for_missing_key(self, tmp_memory):
        assert tmp_memory.get("nonexistent") is None

    def test_set_and_get(self, tmp_memory):
        tmp_memory.set("key1", "value1")
        assert tmp_memory.get("key1") == "value1"

    def test_set_overwrites(self, tmp_memory):
        tmp_memory.set("key1", "old")
        tmp_memory.set("key1", "new")
        assert tmp_memory.get("key1") == "new"

    def test_namespaces(self, tmp_memory):
        tmp_memory.set("key1", "val_a", namespace="ns_a")
        tmp_memory.set("key1", "val_b", namespace="ns_b")
        assert tmp_memory.get("key1", namespace="ns_a") == "val_a"
        assert tmp_memory.get("key1", namespace="ns_b") == "val_b"

    def test_delete(self, tmp_memory):
        tmp_memory.set("key1", "value1")
        assert tmp_memory.delete("key1") is True
        assert tmp_memory.get("key1") is None

    def test_delete_missing(self, tmp_memory):
        assert tmp_memory.delete("nonexistent") is False

    def test_list_keys(self, tmp_memory):
        tmp_memory.set("a", 1)
        tmp_memory.set("b", 2)
        tmp_memory.set("c", 3)
        keys = tmp_memory.list_keys()
        assert sorted(keys) == ["a", "b", "c"]

    def test_list_keys_empty_namespace(self, tmp_memory):
        assert tmp_memory.list_keys("nonexistent") == []

    def test_list_namespaces(self, tmp_memory):
        tmp_memory.set("k", "v", namespace="ns1")
        tmp_memory.set("k", "v", namespace="ns2")
        ns = tmp_memory.list_namespaces()
        assert sorted(ns) == ["ns1", "ns2"]

    def test_search(self, tmp_memory):
        tmp_memory.set("greeting", "hello world")
        tmp_memory.set("farewell", "goodbye world")
        tmp_memory.set("other", "something else")
        results = tmp_memory.search("world")
        assert len(results) == 2
        values = {r.value for r in results}
        assert values == {"hello world", "goodbye world"}

    def test_search_case_insensitive(self, tmp_memory):
        tmp_memory.set("key", "Hello World")
        results = tmp_memory.search("hello")
        assert len(results) == 1

    def test_search_in_namespace(self, tmp_memory):
        tmp_memory.set("k", "hello", namespace="ns1")
        tmp_memory.set("k", "hello", namespace="ns2")
        results = tmp_memory.search("hello", namespace="ns1")
        assert len(results) == 1

    def test_clear_namespace(self, tmp_memory):
        tmp_memory.set("a", 1, namespace="ns1")
        tmp_memory.set("b", 2, namespace="ns2")
        tmp_memory.clear(namespace="ns1")
        assert tmp_memory.get("a", namespace="ns1") is None
        assert tmp_memory.get("b", namespace="ns2") == 2

    def test_clear_all(self, tmp_memory):
        tmp_memory.set("a", 1)
        tmp_memory.set("b", 2)
        tmp_memory.clear()
        assert tmp_memory.list_keys() == []

    def test_persistence(self, tmp_path):
        path = tmp_path / "persist.json"
        mem1 = MemoryManager(storage_path=path)
        mem1.set("key", "value")

        mem2 = MemoryManager(storage_path=path)
        assert mem2.get("key") == "value"

    def test_preserves_created_at_on_update(self, tmp_memory):
        tmp_memory.set("key", "v1")
        entry = tmp_memory._store["default"]["key"]
        created = entry.created_at
        tmp_memory.set("key", "v2")
        entry2 = tmp_memory._store["default"]["key"]
        assert entry2.created_at == created

    def test_metadata(self, tmp_memory):
        tmp_memory.set("key", "val", metadata={"tag": "test"})
        entry = tmp_memory._store["default"]["key"]
        assert entry.metadata == {"tag": "test"}

    def test_complex_values(self, tmp_memory):
        tmp_memory.set("list", [1, 2, 3])
        tmp_memory.set("dict", {"nested": True})
        assert tmp_memory.get("list") == [1, 2, 3]
        assert tmp_memory.get("dict") == {"nested": True}
