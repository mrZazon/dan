from __future__ import annotations

from typing import Any

from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool


@tool
class EchoTool(Tool):

    name = "echo"
    description = "Echoes text."

    async def execute(self, **kwargs: Any) -> ToolResult:
        message = kwargs.get("message", "")
        return ToolResult(
            success=True,
            message=message,
            data={"echo": message},
        )
