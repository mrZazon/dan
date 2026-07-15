from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_CHATS_PATH = Path.home() / ".local" / "share" / "dan" / "chats.json"


class ChatStore:
    """Persistent conversation storage backed by a JSON file.

    Each conversation has:
        id: str          — short UUID
        title: str       — human-readable label
        messages: list   — list of message dicts
        created_at: float — unix timestamp
        updated_at: float — unix timestamp
    """

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or DEFAULT_CHATS_PATH
        self._conversations: list[dict[str, Any]] = []
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def conversations(self) -> list[dict[str, Any]]:
        return self._conversations

    def get(self, conv_id: str) -> dict[str, Any] | None:
        for c in self._conversations:
            if c["id"] == conv_id:
                return c
        return None

    def add(self, conv: dict[str, Any]) -> None:
        conv.setdefault("created_at", time.time())
        conv.setdefault("updated_at", time.time())
        self._conversations.append(conv)
        self._save()

    def update(self, conv_id: str, **changes: Any) -> None:
        conv = self.get(conv_id)
        if conv is None:
            return
        conv.update(changes)
        conv["updated_at"] = time.time()
        self._save()

    def delete(self, conv_id: str) -> bool:
        before = len(self._conversations)
        self._conversations = [c for c in self._conversations if c["id"] != conv_id]
        if len(self._conversations) < before:
            self._save()
            return True
        return False

    def add_message(self, conv_id: str, msg: dict[str, Any]) -> None:
        conv = self.get(conv_id)
        if conv is None:
            return
        conv.setdefault("messages", []).append(msg)
        conv["updated_at"] = time.time()
        self._save()

    def set_title(self, conv_id: str, title: str) -> None:
        self.update(conv_id, title=title)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if not self._path.exists():
            self._conversations = []
            return
        try:
            raw = self._path.read_text()
            data = json.loads(raw)
            self._conversations = data if isinstance(data, list) else []
            logger.debug("Loaded %d conversations from %s", len(self._conversations), self._path)
        except Exception:
            logger.exception("Failed to load chats from %s", self._path)
            self._conversations = []

    def flush(self) -> None:
        """Force an immediate write to disk."""
        self._save()

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._path.write_text(
                json.dumps(self._conversations, indent=2, default=str, ensure_ascii=False)
            )
        except Exception:
            logger.exception("Failed to save chats to %s", self._path)
