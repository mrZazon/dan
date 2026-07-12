from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool

import time


@tool
class HourTool(Tool):

    name = "hour"
    description = "returns current system time"
    aliases = (
        "date",
        "time",
        "hour"
    )
    async def execute(self, **kwargs):

        t = time.strftime("%H:%M:%S", time.localtime())

        return ToolResult(
            success=True,
            message="Current time is: " + t,
            data={
                "time": t
            }
        )