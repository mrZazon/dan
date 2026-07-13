from __future__ import annotations

from abc import ABC, abstractmethod


class Service(ABC):
    """Base class for all D.A.N. services.

    Services contain ALL business logic.
    Tools are thin wrappers that delegate to services.
    """

    name: str = ""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service (connect to system, load resources)."""
        raise NotImplementedError

    @abstractmethod
    async def shutdown(self) -> None:
        """Clean up resources."""
        raise NotImplementedError

    async def health_check(self) -> bool:
        """Check if the service is operational."""
        return True
