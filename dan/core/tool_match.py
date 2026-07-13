from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dan.tools.base import Tool


@dataclass(slots=True)
class ToolMatch:
    """Result of matching a message against a tool."""

    tool: type[Tool]
    score: float

    def __repr__(self) -> str:
        return f"ToolMatch(tool={self.tool.name!r}, score={self.score:.1f})"
