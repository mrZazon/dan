from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProviderResponse:
    """Standard response from a provider."""

    text: str
    model: str = ""
    usage: dict[str, int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderMessage:
    """A message in a conversation."""

    role: str  # "system", "user", "assistant"
    content: str


class Provider(ABC):
    """Model-agnostic provider interface.

    Every external AI dependency belongs behind this interface.
    Changing provider must require ZERO business logic changes.
    """

    name: str = ""
    model: str = ""

    @abstractmethod
    async def complete(
        self,
        messages: list[ProviderMessage],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Generate a completion."""
        raise NotImplementedError

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is available and healthy."""
        raise NotImplementedError

    @abstractmethod
    async def load_model(self, model_name: str) -> None:
        """Load a model into memory."""
        raise NotImplementedError

    @abstractmethod
    async def unload_model(self) -> None:
        """Unload model from memory."""
        raise NotImplementedError

    async def stream(
        self,
        messages: list[ProviderMessage],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream a completion token by token. Default falls back to complete()."""
        resp = await self.complete(messages, temperature, max_tokens, **kwargs)
        yield resp.text

    def is_loaded(self) -> bool:
        """Check if a model is currently loaded."""
        return False
