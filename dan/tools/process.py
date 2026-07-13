from __future__ import annotations
from typing import Any
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool
from dan.services.shell import ShellService


@tool
class ListProcessesTool(Tool):
    name = "list_processes"
    description = "Lists running processes sorted by CPU usage"
    aliases = ("processes", "running processes", "top processes")
    intents = {"list processes": 5, "show processes": 4, "running processes": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("ps aux --sort=-%cpu | head -20")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class KillProcessTool(Tool):
    name = "kill_process"
    description = "Kills a process by PID"
    aliases = ("kill", "terminate", "end process")
    intents = {"kill process": 5, "terminate process": 4, "end process": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        pid = kwargs.get("pid", "")
        result = await self._service.execute(f"kill {pid}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class KillByNameTool(Tool):
    name = "kill_by_name"
    description = "Kills a process by name"
    aliases = ("kill name", "terminate by name")
    intents = {"kill process by name": 5, "kill by name": 4, "terminate by name": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        name = kwargs.get("name", "")
        result = await self._service.execute(f"pkill {name}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ProcessInfoTool(Tool):
    name = "process_info"
    description = "Shows detailed info for a process by PID"
    aliases = ("proc info", "process details")
    intents = {"process info": 5, "process details": 4, "show process info": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        pid = kwargs.get("pid", "")
        result = await self._service.execute(f"ps -p {pid} -o pid,ppid,cmd,%cpu,%mem,etime")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ProcessTreeTool(Tool):
    name = "process_tree"
    description = "Shows the process tree"
    aliases = ("pstree", "tree processes")
    intents = {"process tree": 5, "show process tree": 4, "process hierarchy": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("pstree -p | head -30")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class DiskIOTool(Tool):
    name = "disk_io"
    description = "Shows disk I/O statistics"
    aliases = ("disk stats", "io stats")
    intents = {"disk io": 5, "disk stats": 4, "disk i/o": 4, "io statistics": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("iostat -x 1 1 2>/dev/null || cat /proc/diskstats | head -10")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class OpenFilesTool(Tool):
    name = "open_files"
    description = "Shows open files for a process"
    aliases = ("file descriptors", "open fds")
    intents = {"open files": 5, "file descriptors": 4, "open file descriptors": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        pid = kwargs.get("pid", "")
        result = await self._service.execute(f"ls -la /proc/{pid}/fd 2>/dev/null | head -20")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class NicenessTool(Tool):
    name = "set_priority"
    description = "Changes the priority of a process"
    aliases = ("renice", "change priority", "process priority")
    intents = {"set priority": 5, "change priority": 4, "renice": 4, "process priority": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        pid = kwargs.get("pid", "")
        priority = kwargs.get("priority", "10")
        result = await self._service.execute(f"renice {priority} {pid}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class BackgroundTool(Tool):
    name = "background"
    description = "Runs a command in the background"
    aliases = ("run background", "bg")
    intents = {"run in background": 5, "run background": 4, "background process": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        command = kwargs.get("command", "")
        result = await self._service.execute(f"nohup {command} > /dev/null 2>&1 & echo \"Started in background\"")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class NohupTool(Tool):
    name = "nohup"
    description = "Runs a command with nohup to keep it running after logout"
    aliases = ("no hangup", "persistent")
    intents = {"nohup": 5, "no hangup": 4, "run nohup": 4, "persistent process": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        command = kwargs.get("command", "")
        result = await self._service.execute(f"nohup {command} &")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )
