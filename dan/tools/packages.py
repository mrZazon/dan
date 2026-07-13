from __future__ import annotations
from typing import Any
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool
from dan.services.shell import ShellService


@tool
class AptUpdateTool(Tool):
    name = "apt_update"
    description = "Updates apt package list"
    aliases = ("apt update", "refresh packages")
    intents = {
        "apt update": 5,
        "update packages": 5,
        "refresh packages": 5,
        "package update": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("sudo apt update")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class AptUpgradeTool(Tool):
    name = "apt_upgrade"
    description = "Upgrades all packages"
    aliases = ("apt upgrade", "upgrade packages")
    intents = {
        "apt upgrade": 5,
        "upgrade packages": 5,
        "update all": 5,
        "system upgrade": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("sudo apt upgrade -y")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class AptInstallTool(Tool):
    name = "apt_install"
    description = "Installs a package"
    aliases = ("apt install", "install package")
    intents = {
        "install package": 5,
        "apt install": 5,
        "add package": 4,
        "get package": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        package = kwargs.get("package", "")
        result = await self._service.execute(f"sudo apt install -y {package}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class AptSearchTool(Tool):
    name = "apt_search"
    description = "Searches for a package"
    aliases = ("apt search", "find package")
    intents = {
        "search package": 5,
        "apt search": 5,
        "find package": 5,
        "package search": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        query = kwargs.get("query", "")
        result = await self._service.execute(f"apt search {query}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class AptListTool(Tool):
    name = "apt_list"
    description = "Lists installed packages"
    aliases = ("apt list", "installed packages")
    intents = {
        "list packages": 5,
        "apt list": 5,
        "installed packages": 5,
        "show packages": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("apt list --installed | head -30")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class PipInstallTool(Tool):
    name = "pip_install"
    description = "Installs Python package"
    aliases = ("pip install", "python install")
    intents = {
        "pip install": 5,
        "install python package": 5,
        "python package": 5,
        "pip": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        package = kwargs.get("package", "")
        result = await self._service.execute(f"pip install {package}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class PipListTool(Tool):
    name = "pip_list"
    description = "Lists Python packages"
    aliases = ("pip list", "python packages")
    intents = {
        "pip list": 5,
        "python packages": 5,
        "list python packages": 5,
        "pip packages": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("pip list | head -30")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class NpmInstallTool(Tool):
    name = "npm_install"
    description = "Installs Node package"
    aliases = ("npm install", "node install")
    intents = {
        "npm install": 5,
        "install node package": 5,
        "node package": 5,
        "npm": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        package = kwargs.get("package", "")
        result = await self._service.execute(f"npm install -g {package}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class NpmListTool(Tool):
    name = "npm_list"
    description = "Lists Node packages"
    aliases = ("npm list", "node packages")
    intents = {
        "npm list": 5,
        "node packages": 5,
        "list node packages": 5,
        "npm packages": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("npm list -g --depth=0")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class SnapInstallTool(Tool):
    name = "snap_install"
    description = "Installs snap package"
    aliases = ("snap install", "snap package")
    intents = {
        "snap install": 5,
        "install snap": 5,
        "snap package": 5,
        "snap": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        package = kwargs.get("package", "")
        result = await self._service.execute(f"sudo snap install {package}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )
