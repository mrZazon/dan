from __future__ import annotations
from typing import Any
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool
from dan.services.shell import ShellService


@tool
class ChmodTool(Tool):
    name = "chmod_file"
    description = "Changes file permissions"
    aliases = ("change permissions", "set permissions")
    intents = {
        "change permissions": 5,
        "set permissions": 5,
        "make executable": 4,
        "file permission": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        mode = kwargs.get("mode", "755")
        path = kwargs.get("path", "")
        result = await self._service.execute(f"chmod {mode} {path}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ChownTool(Tool):
    name = "chown"
    description = "Changes file owner"
    aliases = ("change owner", "set owner")
    intents = {
        "change owner": 5,
        "set owner": 5,
        "chown": 5,
        "change ownership": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        owner = kwargs.get("owner", "root")
        path = kwargs.get("path", "")
        result = await self._service.execute(f"chown {owner} {path}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class SudoTool(Tool):
    name = "sudo"
    description = "Runs command as root"
    aliases = ("as root", "superuser")
    intents = {
        "run as root": 5,
        "sudo": 5,
        "superuser": 4,
        "administrator": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        command = kwargs.get("command", "whoami")
        result = await self._service.execute(f"sudo {command}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class PasswdTool(Tool):
    name = "passwd_info"
    description = "Shows password file"
    aliases = ("password file", "users file")
    intents = {
        "password file": 5,
        "show passwd": 5,
        "users file": 4,
        "user list": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("cat /etc/passwd | head -20")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ShadowInfoTool(Tool):
    name = "shadow_info"
    description = "Shows shadow file info"
    aliases = ("shadow", "password info")
    intents = {
        "shadow file": 5,
        "show shadow": 5,
        "password info": 4,
        "user passwords": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("sudo cat /etc/shadow 2>/dev/null | head -5 || echo 'Permission denied'")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class SudoersTool(Tool):
    name = "sudoers"
    description = "Shows sudoers file"
    aliases = ("sudo permissions", "admin users")
    intents = {
        "sudoers": 5,
        "show sudoers": 5,
        "who can sudo": 5,
        "admin users": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("cat /etc/sudoers 2>/dev/null || sudo cat /etc/sudoers 2>/dev/null | head -20 || echo 'Permission denied'")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class GroupsTool(Tool):
    name = "groups"
    description = "Shows user groups"
    aliases = ("user groups", "group list")
    intents = {
        "show groups": 5,
        "user groups": 5,
        "groups": 5,
        "what groups": 4,
        "group membership": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        user = kwargs.get("user", "")
        if user:
            result = await self._service.execute(f"groups {user}")
        else:
            result = await self._service.execute("groups")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class IdTool(Tool):
    name = "id"
    description = "Shows user ID info"
    aliases = ("user id", "uid")
    intents = {
        "user id": 5,
        "show id": 5,
        "uid": 5,
        "who am i id": 4,
        "user info": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        user = kwargs.get("user", "")
        if user:
            result = await self._service.execute(f"id {user}")
        else:
            result = await self._service.execute("id")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class LastLoginTool(Tool):
    name = "last_login"
    description = "Shows last login info"
    aliases = ("last login", "login history")
    intents = {
        "last login": 5,
        "show last login": 5,
        "login history": 5,
        "when did i login": 4,
        "last access": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("last -5")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class Fail2BanTool(Tool):
    name = "fail2ban"
    description = "Shows fail2ban status"
    aliases = ("fail2ban status", "banned ips")
    intents = {
        "fail2ban": 5,
        "banned ips": 5,
        "show fail2ban": 5,
        "security status": 4,
        "blocked ips": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("sudo fail2ban-client status 2>/dev/null || echo 'fail2ban not installed'")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )
