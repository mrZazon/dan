from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""

    name: str
    version: str
    description: str = ""
    author: str = ""
    dependencies: list[str] = field(default_factory=list)


class Plugin(ABC):
    """Base class for D.A.N. plugins.

    Plugins extend D.A.N. with new tools, services, providers,
    and other capabilities. They use lifecycle hooks for initialization
    and cleanup.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the plugin."""

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the plugin."""

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""

    async def on_tool_registered(self, tool_name: str) -> None:  # noqa: B027
        """Hook called when a tool is registered."""

    async def on_tool_executed(self, tool_name: str, success: bool) -> None:  # noqa: B027
        """Hook called after a tool execution."""
