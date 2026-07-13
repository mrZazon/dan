from __future__ import annotations
from typing import Any
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool
from dan.services.shell import ShellService


@tool
class CurrentTimeTool(Tool):
    name = "current_time"
    description = "Shows the current time"
    aliases = ("time", "what time")
    intents = {"what time": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute('date +"%H:%M:%S"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class CurrentDateTool(Tool):
    name = "current_date"
    description = "Shows the current date"
    aliases = ("date", "what date")
    intents = {"what date": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute('date +"%Y-%m-%d"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class DateTimeTool(Tool):
    name = "date_time"
    description = "Shows the current date and time"
    aliases = ("datetime", "date and time")
    intents = {"date and time": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute('date +"%Y-%m-%d %H:%M:%S %Z"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class UnixTimestampTool(Tool):
    name = "unix_timestamp"
    description = "Shows the current Unix timestamp"
    aliases = ("epoch", "unix timestamp")
    intents = {"unix timestamp": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("date +%s")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class TimezoneTool(Tool):
    name = "timezone"
    description = "Shows the system timezone"
    aliases = ("tz", "timezone")
    intents = {"timezone": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("timedatectl show --property=Timezone --value 2>/dev/null || cat /etc/timezone 2>/dev/null || date +%Z")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class WeekdayTool(Tool):
    name = "weekday"
    description = "Shows the current day of the week"
    aliases = ("day", "what day")
    intents = {"what day": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute('date +"%A"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class DayOfYearTool(Tool):
    name = "day_of_year"
    description = "Shows the current day of the year"
    aliases = ("doy", "day of year")
    intents = {"day of year": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute('date +"%j"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class CalendarTool(Tool):
    name = "calendar"
    description = "Shows the current month's calendar"
    aliases = ("cal", "calendar")
    intents = {"calendar": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("cal")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class EpochConvertTool(Tool):
    name = "epoch_convert"
    description = "Converts an epoch timestamp to a human-readable date"
    aliases = ("convert epoch", "epoch to date")
    intents = {"convert epoch": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        timestamp = kwargs.get("timestamp", "")
        result = await self._service.execute(f'date -d @{timestamp} +"%Y-%m-%d %H:%M:%S %Z"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class DaysUntilTool(Tool):
    name = "days_until"
    description = "Shows the number of days until a given date"
    aliases = ("days left", "days until")
    intents = {"days until": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        date = kwargs.get("date", "")
        result = await self._service.execute(f'echo $(( ($(date -d "{date}" +%s) - $(date +%s)) / 86400 )) days')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class WeekNumberTool(Tool):
    name = "week_number"
    description = "Shows the current ISO week number"
    aliases = ("week", "week number")
    intents = {"week number": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute('date +"%V"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})
