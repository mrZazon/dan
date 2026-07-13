from __future__ import annotations
from typing import Any
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool
from dan.services.shell import ShellService


@tool
class VmstatTool(Tool):
    name = "vmstat"
    description = "Shows virtual memory statistics"
    aliases = ("virtual memory", "vm stats")
    intents = {
        "vmstat": 5,
        "virtual memory": 5,
        "memory stats": 5,
        "memory statistics": 4,
        "swap usage": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("vmstat 1 5")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class IostatTool(Tool):
    name = "iostat"
    description = "Shows IO statistics"
    aliases = ("io stats", "disk io")
    intents = {
        "iostat": 5,
        "io statistics": 5,
        "disk io": 5,
        "io stats": 5,
        "disk performance": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("iostat 1 3")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class DstatTool(Tool):
    name = "dstat"
    description = "Shows system resource stats"
    aliases = ("resource stats", "system stats")
    intents = {
        "dstat": 5,
        "resource stats": 5,
        "system stats": 5,
        "combined stats": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("dstat 1 5")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class SarTool(Tool):
    name = "sar"
    description = "Shows system activity reporter"
    aliases = ("system activity", "historical stats")
    intents = {
        "sar": 5,
        "system activity": 5,
        "historical stats": 4,
        "performance history": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("sar -u 1 5")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class MpstatTool(Tool):
    name = "mpstat"
    description = "Shows multi-processor statistics"
    aliases = ("cpu stats", "processor stats")
    intents = {
        "mpstat": 5,
        "cpu stats": 5,
        "processor stats": 5,
        "per cpu": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("mpstat 1 5")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class PidstatTool(Tool):
    name = "pidstat"
    description = "Shows per-process statistics"
    aliases = ("process stats", "per process")
    intents = {
        "pidstat": 5,
        "per process stats": 5,
        "process statistics": 5,
        "process performance": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("pidstat 1 5")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class NstatTool(Tool):
    name = "nstat"
    description = "Shows network statistics"
    aliases = ("net stats", "network counters")
    intents = {
        "nstat": 5,
        "network stats": 5,
        "net statistics": 5,
        "network counters": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("nstat")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class IfstatTool(Tool):
    name = "ifstat"
    description = "Shows interface statistics"
    aliases = ("interface stats", "nic stats")
    intents = {
        "ifstat": 5,
        "interface stats": 5,
        "nic stats": 5,
        "network interface stats": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("ifstat 1 5")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class CollectlTool(Tool):
    name = "collectl"
    description = "Collects system data"
    aliases = ("collect", "data collection")
    intents = {
        "collectl": 5,
        "collect data": 5,
        "system monitor": 4,
        "data collection": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("collectl -c 5 -s c")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class SysstatTool(Tool):
    name = "sysstat"
    description = "Shows system statistics summary"
    aliases = ("system summary", "sys stats")
    intents = {
        "sysstat": 5,
        "system summary": 5,
        "sys stats": 4,
        "system overview": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("uptime && free -h && df -h / && cat /proc/loadavg")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )
