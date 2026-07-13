from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """A single memory entry."""

    key: str
    value: Any
    namespace: str = "default"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


class MemoryManager:
    """Persistent memory system for D.A.N.

    Stores key-value pairs with namespaces, metadata, and TTL support.
    Backed by a JSON file for persistence.
    """

    def __init__(self, storage_path: Path | None = None) -> None:
        self._storage_path = storage_path or Path("dan_memory.json")
        self._store: dict[str, dict[str, MemoryEntry]] = {}
        self._load()

    def _load(self) -> None:
        """Load memory from disk."""
        if self._storage_path.exists():
            try:
                data = json.loads(self._storage_path.read_text())
                for namespace, entries in data.items():
                    self._store[namespace] = {}
                    for key, entry_data in entries.items():
                        self._store[namespace][key] = MemoryEntry(
                            key=key,
                            value=entry_data["value"],
                            namespace=namespace,
                            created_at=entry_data.get("created_at", time.time()),
                            updated_at=entry_data.get("updated_at", time.time()),
                            metadata=entry_data.get("metadata", {}),
                        )
                logger.debug("Loaded memory from %s", self._storage_path)
            except Exception:
                logger.exception("Failed to load memory from %s", self._storage_path)

    def _save(self) -> None:
        """Persist memory to disk."""
        data: dict[str, dict[str, Any]] = {}
        for namespace, entries in self._store.items():
            data[namespace] = {}
            for key, entry in entries.items():
                data[namespace][key] = {
                    "value": entry.value,
                    "created_at": entry.created_at,
                    "updated_at": entry.updated_at,
                    "metadata": entry.metadata,
                }
        try:
            self._storage_path.write_text(json.dumps(data, indent=2, default=str))
        except Exception:
            logger.exception("Failed to save memory to %s", self._storage_path)

    def get(self, key: str, namespace: str = "default") -> Any | None:
        """Get a value by key and namespace."""
        entry = self._store.get(namespace, {}).get(key)
        return entry.value if entry else None

    def set(
        self,
        key: str,
        value: Any,
        namespace: str = "default",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Set a value with optional metadata."""
        now = time.time()
        if namespace not in self._store:
            self._store[namespace] = {}

        existing = self._store[namespace].get(key)
        self._store[namespace][key] = MemoryEntry(
            key=key,
            value=value,
            namespace=namespace,
            created_at=existing.created_at if existing else now,
            updated_at=now,
            metadata=metadata or (existing.metadata if existing else {}),
        )
        self._save()

    def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete a key from a namespace. Returns True if deleted."""
        if namespace in self._store and key in self._store[namespace]:
            del self._store[namespace][key]
            self._save()
            return True
        return False

    def list_keys(self, namespace: str = "default") -> list[str]:
        """List all keys in a namespace."""
        return list(self._store.get(namespace, {}).keys())

    def list_namespaces(self) -> list[str]:
        """List all namespaces."""
        return list(self._store.keys())

    def search(self, query: str, namespace: str | None = None) -> list[MemoryEntry]:
        """Search for entries where the value contains the query string."""
        results: list[MemoryEntry] = []
        namespaces = [namespace] if namespace else list(self._store.keys())
        for ns in namespaces:
            for entry in self._store.get(ns, {}).values():
                if query.lower() in str(entry.value).lower():
                    results.append(entry)
        return results

    def clear(self, namespace: str | None = None) -> None:
        """Clear entries from a namespace or all namespaces."""
        if namespace:
            self._store.pop(namespace, None)
        else:
            self._store.clear()
        self._save()
