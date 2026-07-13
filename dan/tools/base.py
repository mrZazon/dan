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

    name: str = ""
    description: str = ""
    __dan_tool__: bool = False

    aliases: tuple[str, ...] = ()
    intents: dict[str, float] = {}

    @classmethod
    def score(cls, message: str) -> float:
        """
        Calculate how well this tool matches a message.
        """

        message = message.lower()

        score = 0.0

        # Weak matches
        for alias in cls.aliases:
            if alias in message:
                score += 1

        # Strong matches
        for phrase, points in cls.intents.items():
            if phrase in message:
                score += points

        return score

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """
        Execute the tool.
        """
        raise NotImplementedError
