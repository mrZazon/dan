from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ToolResult:
    """
    Standard response returned by every Tool.
    """

    success: bool
    message: str = ""
    data: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)


class Tool(ABC):
    """
    Base class for every D.A.N. capability.
    """

    # Unique identifier
    name: str = ""

    # Human-readable description
    description: str = ""

    # Optional aliases
    aliases: tuple[str, ...] = ()

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """
        Execute the tool.
        """
        raise NotImplementedError