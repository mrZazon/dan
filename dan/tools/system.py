from __future__ import annotations
from typing import Any
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool
from dan.services.shell import ShellService


@tool
class CpuInfoTool(Tool):
    name = "cpu_info"
    description = "Shows CPU information"
    aliases = ("cpu", "processor", "cpuinfo")
    intents = {
        "what is my cpu": 5,
        "show cpu info": 5,
        "cpu information": 5,
        "processor info": 4,
        "show processor": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("lscpu | head -20")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class MemoryInfoTool(Tool):
    name = "memory_info"
    description = "Shows memory usage"
    aliases = ("memory", "mem", "ram")
    intents = {
        "show memory": 5,
        "memory usage": 5,
        "ram usage": 4,
        "how much memory": 4,
        "free memory": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("free -h")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class DiskInfoTool(Tool):
    name = "disk_info"
    description = "Shows disk usage"
    aliases = ("disk", "disk space", "storage")
    intents = {
        "disk space": 5,
        "show disk": 5,
        "disk usage": 5,
        "storage info": 4,
        "how much disk": 4,
        "free disk space": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("df -h")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class SystemInfoTool(Tool):
    name = "system_info"
    description = "Shows system information"
    aliases = ("system", "sysinfo", "machine")
    intents = {
        "system information": 5,
        "show system info": 5,
        "what is this system": 4,
        "machine info": 4,
        "system details": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("uname -a && hostnamectl")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class UptimeTool(Tool):
    name = "uptime"
    description = "Shows system uptime"
    aliases = ("up time", "how long running")
    intents = {
        "how long": 5,
        "system uptime": 5,
        "how long has it been running": 5,
        "uptime": 5,
        "when was it started": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("uptime")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class WhoamiTool(Tool):
    name = "whoami"
    description = "Shows current user"
    aliases = ("current user", "my username")
    intents = {
        "who am i": 5,
        "what is my username": 5,
        "current user": 5,
        "whoami": 5,
        "my user": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("whoami")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class UsersTool(Tool):
    name = "users"
    description = "Shows logged in users"
    aliases = ("logged in", "active users")
    intents = {
        "who is logged in": 5,
        "logged in users": 5,
        "active users": 4,
        "who is using": 3,
        "current users": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("who")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class HostnameTool(Tool):
    name = "hostname"
    description = "Shows hostname"
    aliases = ("host name", "machine name")
    intents = {
        "what is my hostname": 5,
        "show hostname": 5,
        "hostname": 5,
        "machine name": 4,
        "what is this host": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("hostname -f")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class KernelTool(Tool):
    name = "kernel"
    description = "Shows kernel version"
    aliases = ("kernel version", "uname")
    intents = {
        "kernel version": 5,
        "what kernel": 5,
        "uname": 5,
        "show kernel": 4,
        "linux version": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("uname -r")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ArchTool(Tool):
    name = "arch"
    description = "Shows system architecture"
    aliases = ("architecture", "platform")
    intents = {
        "architecture": 5,
        "what architecture": 5,
        "system arch": 5,
        "platform": 4,
        "64 bit or 32 bit": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("uname -m")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class LsblkTool(Tool):
    name = "lsblk"
    description = "Shows block devices"
    aliases = ("block devices", "partitions")
    intents = {
        "block devices": 5,
        "show partitions": 5,
        "lsblk": 5,
        "disk partitions": 4,
        "storage devices": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("lsblk")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class MountInfoTool(Tool):
    name = "mount_info"
    description = "Shows mount points"
    aliases = ("mounts", "mounted")
    intents = {
        "mount points": 5,
        "show mounts": 5,
        "what is mounted": 4,
        "mounted filesystems": 3,
        "mount info": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("mount | grep -E '^/' | head -20")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class EnvVarTool(Tool):
    name = "env_var"
    description = "Shows an environment variable"
    aliases = ("env", "environment")
    intents = {
        "environment variable": 5,
        "env var": 5,
        "show environment": 4,
        "get variable": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        variable = kwargs.get("variable", "PATH")
        result = await self._service.execute(f"echo ${variable}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class TopProcessesTool(Tool):
    name = "top_processes"
    description = "Shows top processes by CPU"
    aliases = ("top cpu", "cpu processes")
    intents = {
        "top processes": 5,
        "cpu processes": 5,
        "what is using cpu": 4,
        "processes by cpu": 3,
        "most cpu": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("ps aux --sort=-%cpu | head -11")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class TopMemoryTool(Tool):
    name = "top_memory"
    description = "Shows top processes by memory"
    aliases = ("top mem", "memory processes")
    intents = {
        "top memory": 5,
        "memory processes": 5,
        "what is using memory": 4,
        "processes by memory": 3,
        "most memory": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("ps aux --sort=-%mem | head -11")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )
