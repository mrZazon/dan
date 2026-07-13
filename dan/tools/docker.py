from __future__ import annotations
from typing import Any
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool
from dan.services.shell import ShellService


@tool
class DockerPsTool(Tool):
    name = "docker_ps"
    description = "Lists Docker containers"
    aliases = ("containers", "docker ps")
    intents = {"docker ps": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute('docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class DockerImagesTool(Tool):
    name = "docker_images"
    description = "Lists Docker images"
    aliases = ("images", "docker images")
    intents = {"docker images": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute('docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class DockerRunTool(Tool):
    name = "docker_run"
    description = "Runs a Docker container"
    aliases = ("run container", "docker run")
    intents = {"docker run": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        image = kwargs.get("image", "")
        name = kwargs.get("name", "")
        cmd = f"docker run -d {('--name ' + name) if name else ''} {image}"
        result = await self._service.execute(cmd)
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class DockerStopTool(Tool):
    name = "docker_stop"
    description = "Stops a Docker container"
    aliases = ("stop container", "docker stop")
    intents = {"docker stop": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        container = kwargs.get("container", "")
        result = await self._service.execute(f"docker stop {container}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class DockerStartTool(Tool):
    name = "docker_start"
    description = "Starts a Docker container"
    aliases = ("start container", "docker start")
    intents = {"docker start": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        container = kwargs.get("container", "")
        result = await self._service.execute(f"docker start {container}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class DockerRmTool(Tool):
    name = "docker_rm"
    description = "Removes a Docker container"
    aliases = ("remove container", "docker rm")
    intents = {"docker rm": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        container = kwargs.get("container", "")
        result = await self._service.execute(f"docker rm {container}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class DockerLogsTool(Tool):
    name = "docker_logs"
    description = "Shows Docker container logs"
    aliases = ("container logs", "docker logs")
    intents = {"docker logs": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        container = kwargs.get("container", "")
        result = await self._service.execute(f"docker logs --tail 50 {container}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class DockerExecTool(Tool):
    name = "docker_exec"
    description = "Executes a command in a Docker container"
    aliases = ("exec container", "docker exec")
    intents = {"docker exec": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        container = kwargs.get("container", "")
        command = kwargs.get("command", "")
        result = await self._service.execute(f"docker exec {container} {command}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class DockerInspectTool(Tool):
    name = "docker_inspect"
    description = "Inspects a Docker container"
    aliases = ("inspect container", "docker inspect")
    intents = {"docker inspect": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        container = kwargs.get("container", "")
        result = await self._service.execute(f"docker inspect {container} | python3 -m json.tool | head -30")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class DockerComposeUpTool(Tool):
    name = "docker_compose_up"
    description = "Starts a Docker Compose stack"
    aliases = ("compose up", "docker compose up")
    intents = {"docker compose up": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", ".")
        result = await self._service.execute(f"docker compose -f {path}/docker-compose.yml up -d")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class DockerComposeDownTool(Tool):
    name = "docker_compose_down"
    description = "Stops a Docker Compose stack"
    aliases = ("compose down", "docker compose down")
    intents = {"docker compose down": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", ".")
        result = await self._service.execute(f"docker compose -f {path}/docker-compose.yml down")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})
