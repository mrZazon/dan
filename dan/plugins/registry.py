from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dan.plugins.base import Plugin, PluginMetadata

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Registry for managing plugins.

    Handles plugin lifecycle: discovery, initialization, and shutdown.
    """

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}
        self._initialized: dict[str, bool] = {}

    def register(self, plugin: Plugin) -> None:
        """Register a plugin."""
        metadata = plugin.get_metadata()
        if metadata.name in self._plugins:
            logger.warning(
                "Plugin %s already registered, replacing", metadata.name
            )
        self._plugins[metadata.name] = plugin
        self._initialized[metadata.name] = False
        logger.debug("Registered plugin: %s v%s", metadata.name, metadata.version)

    def get(self, name: str) -> Plugin | None:
        """Get a plugin by name."""
        return self._plugins.get(name)

    def remove(self, name: str) -> bool:
        """Remove a plugin. Returns True if removed."""
        if name in self._plugins:
            del self._plugins[name]
            self._initialized.pop(name, None)
            return True
        return False

    async def initialize_all(self) -> None:
        """Initialize all registered plugins."""
        for name, plugin in self._plugins.items():
            if not self._initialized.get(name, False):
                try:
                    await plugin.initialize()
                    self._initialized[name] = True
                    logger.info("Initialized plugin: %s", name)
                except Exception:
                    logger.exception("Failed to initialize plugin: %s", name)

    async def shutdown_all(self) -> None:
        """Shutdown all initialized plugins."""
        for name, plugin in self._plugins.items():
            if self._initialized.get(name, False):
                try:
                    await plugin.shutdown()
                    self._initialized[name] = False
                    logger.info("Shut down plugin: %s", name)
                except Exception:
                    logger.exception("Failed to shutdown plugin: %s", name)

    def list_plugins(self) -> list[PluginMetadata]:
        """List metadata for all registered plugins."""
        return [p.get_metadata() for p in self._plugins.values()]

    def names(self) -> list[str]:
        """List all plugin names."""
        return list(self._plugins.keys())

    def is_initialized(self, name: str) -> bool:
        """Check if a plugin is initialized."""
        return self._initialized.get(name, False)
