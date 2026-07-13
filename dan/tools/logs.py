from __future__ import annotations
from typing import Any
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool
from dan.services.shell import ShellService


@tool
class LogTailTool(Tool):
    name = "log_tail"
    description = "Shows end of log file"
    aliases = ("tail", "end of file")
    intents = {
        "tail log": 5,
        "show end of file": 5,
        "tail": 5,
        "end of file": 5,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        file = kwargs.get("file", "/var/log/syslog")
        lines = kwargs.get("lines", "50")
        result = await self._service.execute(f"tail -n {lines} {file}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class LogHeadTool(Tool):
    name = "log_head"
    description = "Shows beginning of log file"
    aliases = ("head", "start of file")
    intents = {
        "head log": 5,
        "show start of file": 5,
        "head": 5,
        "beginning of file": 5,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        file = kwargs.get("file", "/var/log/syslog")
        lines = kwargs.get("lines", "50")
        result = await self._service.execute(f"head -n {lines} {file}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class LogGrepTool(Tool):
    name = "log_grep"
    description = "Searches in log files"
    aliases = ("grep log", "search log")
    intents = {
        "grep log": 5,
        "search log": 5,
        "find in log": 5,
        "log search": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        pattern = kwargs.get("pattern", "error")
        file = kwargs.get("file", "/var/log/syslog")
        result = await self._service.execute(f"grep -i '{pattern}' {file} | tail -20")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class LogTailfTool(Tool):
    name = "log_tailf"
    description = "Follows log file in real time"
    aliases = ("tailf", "follow log")
    intents = {
        "tailf": 5,
        "follow log": 5,
        "real time log": 5,
        "live log": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        file = kwargs.get("file", "/var/log/syslog")
        result = await self._service.execute(f"timeout 5 tailf {file}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class LogWcTool(Tool):
    name = "log_wc"
    description = "Counts lines in log"
    aliases = ("count lines", "log count")
    intents = {
        "count lines": 5,
        "log lines": 5,
        "how many lines": 5,
        "line count": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        file = kwargs.get("file", "/var/log/syslog")
        result = await self._service.execute(f"wc -l {file}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class DmesgTool(Tool):
    name = "dmesg"
    description = "Shows kernel ring buffer"
    aliases = ("kernel log", "boot log")
    intents = {
        "dmesg": 5,
        "kernel log": 5,
        "boot log": 5,
        "kernel messages": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("dmesg | tail -30")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class JournalctlTool(Tool):
    name = "journalctl"
    description = "Shows systemd journal"
    aliases = ("systemd journal", "system log")
    intents = {
        "journalctl": 5,
        "system log": 5,
        "systemd journal": 5,
        "show journal": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("journalctl -n 50 --no-pager")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class LogErrorsTool(Tool):
    name = "log_errors"
    description = "Shows errors from logs"
    aliases = ("error log", "find errors")
    intents = {
        "error log": 5,
        "find errors": 5,
        "show errors": 5,
        "log errors": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        file = kwargs.get("file", "/var/log/syslog")
        result = await self._service.execute(f"grep -i 'error\\|fail\\|critical' {file} | tail -20")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class LastLoginsTool(Tool):
    name = "last_logins"
    description = "Shows last login entries"
    aliases = ("last logins", "login log")
    intents = {
        "last logins": 5,
        "login log": 5,
        "who logged in": 5,
        "login history": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("last -20")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class AuthLogTool(Tool):
    name = "auth_log"
    description = "Shows authentication log"
    aliases = ("auth log", "auth logs")
    intents = {
        "auth log": 5,
        "authentication log": 5,
        "ssh log": 4,
        "security log": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("sudo tail -30 /var/log/auth.log 2>/dev/null || sudo journalctl -u sshd -n 30 --no-pager")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )
