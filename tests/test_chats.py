import json
import time

import pytest

from dan.memory.chats import ChatStore


class TestChatStore:
    @pytest.fixture
    def store(self, tmp_path):
        return ChatStore(path=tmp_path / "test_chats.json")

    def test_empty_store(self, store):
        assert store.conversations == []

    def test_add_conversation(self, store):
        conv = {"id": "abc123", "title": "Chat 1", "messages": []}
        store.add(conv)
        assert len(store.conversations) == 1
        assert store.get("abc123") is conv

    def test_get_returns_none_for_missing(self, store):
        assert store.get("nonexistent") is None

    def test_update_conversation(self, store):
        conv = {"id": "abc123", "title": "Chat 1", "messages": []}
        store.add(conv)
        store.update("abc123", title="Updated Chat")
        assert store.get("abc123")["title"] == "Updated Chat"

    def test_update_missing(self, store):
        store.update("nonexistent", title="Nope")
        assert len(store.conversations) == 0

    def test_delete_conversation(self, store):
        conv = {"id": "abc123", "title": "Chat 1", "messages": []}
        store.add(conv)
        assert store.delete("abc123") is True
        assert store.get("abc123") is None

    def test_delete_missing(self, store):
        assert store.delete("nonexistent") is False

    def test_add_message(self, store):
        conv = {"id": "abc123", "title": "Chat 1", "messages": []}
        store.add(conv)
        msg = {"type": "user", "text": "hello"}
        store.add_message("abc123", msg)
        assert len(store.get("abc123")["messages"]) == 1
        assert store.get("abc123")["messages"][0]["text"] == "hello"

    def test_add_message_sets_msg_id_and_timestamp(self, store):
        conv = {"id": "abc123", "title": "Chat 1", "messages": []}
        store.add(conv)
        msg = {"type": "user", "text": "hello"}
        store.add_message("abc123", msg)
        saved = store.get("abc123")["messages"][0]
        assert "msg_id" in saved
        assert "timestamp" in saved

    def test_add_message_skips_duplicate_msg_id(self, store):
        conv = {"id": "abc123", "title": "Chat 1", "messages": []}
        store.add(conv)
        msg = {"type": "user", "text": "hello", "msg_id": "dup1"}
        store.add_message("abc123", msg)
        store.add_message("abc123", msg)
        assert len(store.get("abc123")["messages"]) == 1

    def test_add_message_respects_existing_msg_id(self, store):
        conv = {"id": "abc123", "title": "Chat 1", "messages": []}
        store.add(conv)
        msg1 = {"type": "user", "text": "first", "msg_id": "id1"}
        msg2 = {"type": "user", "text": "second", "msg_id": "id2"}
        store.add_message("abc123", msg1)
        store.add_message("abc123", msg2)
        assert len(store.get("abc123")["messages"]) == 2

    def test_add_message_to_missing_conv(self, store):
        store.add_message("nonexistent", {"type": "user", "text": "hello"})
        assert len(store.conversations) == 0

    def test_set_title(self, store):
        conv = {"id": "abc123", "title": "Chat 1", "messages": []}
        store.add(conv)
        store.set_title("abc123", "New Title")
        assert store.get("abc123")["title"] == "New Title"

    def test_conversations_sorted_by_updated_at(self, tmp_path):
        path = tmp_path / "sorted.json"
        older = {
            "id": "old", "title": "Old", "messages": [],
            "created_at": 100.0, "updated_at": 100.0,
        }
        newer = {
            "id": "new", "title": "New", "messages": [],
            "created_at": 200.0, "updated_at": 200.0,
        }
        path.write_text(json.dumps([older, newer]))
        store = ChatStore(path=path)
        assert store.conversations[0]["id"] == "new"
        assert store.conversations[1]["id"] == "old"

    def test_flush_persists(self, tmp_path):
        path = tmp_path / "flush.json"
        store = ChatStore(path=path)
        conv = {"id": "abc123", "title": "Chat 1", "messages": []}
        store.add(conv)
        store.flush()
        raw = json.loads(path.read_text())
        assert len(raw) == 1
        assert raw[0]["id"] == "abc123"

    def test_updated_at_bumps_on_add_message(self, store):
        conv = {"id": "abc123", "title": "Chat 1", "messages": []}
        store.add(conv)
        original = conv["updated_at"]
        time.sleep(0.01)
        store.add_message("abc123", {"type": "user", "text": "hi"})
        assert conv["updated_at"] > original

    def test_persistence(self, tmp_path):
        path = tmp_path / "persist.json"
        store1 = ChatStore(path=path)
        conv = {"id": "abc123", "title": "Chat 1", "messages": []}
        store1.add(conv)
        store1.add_message("abc123", {"type": "user", "text": "hello"})

        store2 = ChatStore(path=path)
        assert len(store2.conversations) == 1
        assert store2.get("abc123") is not None
        assert len(store2.get("abc123")["messages"]) == 1
        assert store2.get("abc123")["messages"][0]["text"] == "hello"

    def test_corrupted_file(self, tmp_path):
        path = tmp_path / "corrupt.json"
        path.write_text("{invalid json}")
        store = ChatStore(path=path)
        assert store.conversations == []

    def test_empty_file(self, tmp_path):
        path = tmp_path / "empty.json"
        store = ChatStore(path=path)
        assert store.conversations == []
