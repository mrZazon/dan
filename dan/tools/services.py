from __future__ import annotations
from typing import Any
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool
from dan.services.shell import ShellService


@tool
class ServiceStatusTool(Tool):
    name = "service_status"
    description = "Shows service status"
    aliases = ("systemctl status", "service info")
    intents = {
        "service status": 5,
        "show service": 5,
        "is service running": 5,
        "systemctl": 5,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        service = kwargs.get("service", "ssh")
        result = await self._service.execute(f"systemctl status {service}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ServiceStartTool(Tool):
    name = "service_start"
    description = "Starts a service"
    aliases = ("start service", "systemctl start")
    intents = {
        "start service": 5,
        "service start": 5,
        "systemctl start": 5,
        "turn on": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        service = kwargs.get("service", "")
        result = await self._service.execute(f"sudo systemctl start {service}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ServiceStopTool(Tool):
    name = "service_stop"
    description = "Stops a service"
    aliases = ("stop service", "systemctl stop")
    intents = {
        "stop service": 5,
        "service stop": 5,
        "systemctl stop": 5,
        "turn off": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        service = kwargs.get("service", "")
        result = await self._service.execute(f"sudo systemctl stop {service}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ServiceRestartTool(Tool):
    name = "service_restart"
    description = "Restarts a service"
    aliases = ("restart service", "systemctl restart")
    intents = {
        "restart service": 5,
        "service restart": 5,
        "systemctl restart": 5,
        "restart": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        service = kwargs.get("service", "")
        result = await self._service.execute(f"sudo systemctl restart {service}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ServiceEnableTool(Tool):
    name = "service_enable"
    description = "Enables a service at boot"
    aliases = ("enable service", "systemctl enable")
    intents = {
        "enable service": 5,
        "service enable": 5,
        "systemctl enable": 5,
        "auto start": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        service = kwargs.get("service", "")
        result = await self._service.execute(f"sudo systemctl enable {service}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ServiceDisableTool(Tool):
    name = "service_disable"
    description = "Disables a service at boot"
    aliases = ("disable service", "systemctl disable")
    intents = {
        "disable service": 5,
        "service disable": 5,
        "systemctl disable": 5,
        "no auto start": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        service = kwargs.get("service", "")
        result = await self._service.execute(f"sudo systemctl disable {service}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ServiceListTool(Tool):
    name = "service_list"
    description = "Lists all services"
    aliases = ("list services", "systemctl list")
    intents = {
        "list services": 5,
        "show services": 5,
        "all services": 5,
        "systemctl list": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("systemctl list-units --type=service | head -30")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ServiceLogsTool(Tool):
    name = "service_logs"
    description = "Shows service logs"
    aliases = ("journalctl", "service journal")
    intents = {
        "service logs": 5,
        "show logs": 5,
        "journalctl": 5,
        "service journal": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        service = kwargs.get("service", "")
        result = await self._service.execute(f"journalctl -u {service} -n 20 --no-pager")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ServiceEnabledTool(Tool):
    name = "service_enabled"
    description = "Checks if service is enabled"
    aliases = ("is enabled", "enabled at boot")
    intents = {
        "is service enabled": 5,
        "service enabled": 5,
        "enabled at boot": 5,
        "auto start status": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        service = kwargs.get("service", "")
        result = await self._service.execute(f"systemctl is-enabled {service}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ServiceMaskTool(Tool):
    name = "service_mask"
    description = "Masks a service"
    aliases = ("mask service", "systemctl mask")
    intents = {
        "mask service": 5,
        "service mask": 5,
        "systemctl mask": 5,
        "prevent start": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        service = kwargs.get("service", "")
        result = await self._service.execute(f"sudo systemctl mask {service}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )
