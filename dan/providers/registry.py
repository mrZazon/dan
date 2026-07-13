from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dan.providers.base import Provider

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Manages model providers.

    Ollama is the default provider.
    """

    def __init__(self) -> None:
        self._providers: dict[str, Provider] = {}
        self._default: str = "ollama"

    def register(self, provider: Provider) -> None:
        """Register a provider."""
        self._providers[provider.name] = provider
        logger.debug("Registered provider: %s", provider.name)

    def get(self, name: str | None = None) -> Provider:
        """Get a provider by name, or the default.

        Args:
            name: Provider name. Uses default if None.

        Raises:
            KeyError: If provider not found.
        """
        if name is None:
            name = self._default
        if name not in self._providers:
            raise KeyError(f"Provider '{name}' not registered. Available: {self.names()}")
        return self._providers[name]

    def set_default(self, name: str) -> None:
        """Set the default provider."""
        if name not in self._providers:
            raise ValueError(f"Provider '{name}' not registered")
        self._default = name

    def names(self) -> list[str]:
        """Return list of registered provider names."""
        return sorted(self._providers.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._providers

    def __len__(self) -> int:
        return len(self._providers)
