from __future__ import annotations

import time
from typing import Any

from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool


@tool
class HourTool(Tool):

    name = "hour"
    description = "Returns current system time."
    aliases = (
        "time",
        "hour",
        "clock",
        "date",
        "datetime",
        "watch",
        "schedule",
    )

    intents = {
        "what time is it": 5,
        "what is the time": 5,
        "what's the time": 5,
        "what's the current time": 5,
        "tell me the time": 5,
        "tell me what time it is": 5,
        "can you tell me the time": 5,
        "could you tell me the time": 5,
        "do you know the time": 5,
        "please tell me the time": 5,
        "give me the current time": 5,
        "show me the current time": 5,
        "display the current time": 5,
        "current time": 5,
        "current hour": 5,
        "current date and time": 5,
        "right now time": 4,
        "time right now": 5,
        "what time do we have": 4,
        "what hour are we in": 4,
        "which hour is it": 4,
        "tell me the hour": 4,
        "check the clock": 4,
        "look at the clock": 4,
        "read the clock": 4,
        "check time": 4,
        "check current time": 5,
        "show clock": 3,
        "open clock": 2,
        "time now": 4,
        "clock now": 4,
        "hour now": 3,
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        t = time.strftime("%H:%M:%S", time.localtime())
        return ToolResult(
            success=True,
            message="Current time is: " + t,
            data={"time": t},
        )
