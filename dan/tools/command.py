from __future__ import annotations

from typing import Any

from dan.services.shell import ShellService
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool


@tool
class CommandTool(Tool):
    """Execute a single shell command.

    Delegates to ShellService for execution.
    Stateless: creates a new shell process for each execution.
    """

    name = "command"
    description = "Execute a shell command."

    aliases = (
        "command",
        "cmd",
        "shell",
        "bash",
        "terminal",
        "console",
        "cli",
        "command line",
        "prompt",
    )

    intents = {
        "execute": 3,
        "run": 3,
        "ping": 5,
        "curl": 5,
        "wget": 5,
        "ls": 5,
        "cat": 5,
        "grep": 5,
        "find": 5,
        "mkdir": 5,
        "rm": 5,
        "cp": 5,
        "mv": 5,
        "chmod": 5,
        "chown": 5,
        "apt": 5,
        "apt-get": 5,
        "yum": 5,
        "dnf": 5,
        "pacman": 5,
        "pip": 5,
        "npm": 5,
        "node": 5,
        "python": 5,
        "python3": 5,
        "git": 5,
        "docker": 5,
        "ssh": 5,
        "scp": 5,
        "rsync": 5,
        "tar": 5,
        "zip": 5,
        "unzip": 5,
        "open terminal": 5,
        "open the terminal": 5,
        "launch terminal": 4,
        "start terminal": 4,
        "use terminal": 4,
        "use the terminal": 4,
        "open shell": 4,
        "open bash": 4,
        "open command line": 4,
        "run this": 3,
        "execute this": 3,
        "make this run": 3,
        "run it": 3,
        "execute it": 3,
        "launch this": 3,
        "run a system command": 5,
        "execute a system command": 5,
        "perform a shell command": 5,
        "use the shell": 4,
        "type this command": 4,
        "enter this command": 4,
        "show terminal": 3,
        "give me a terminal": 3,
        "i need the terminal": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        command = kwargs.get("command") or kwargs.get("message")

        if not command:
            return ToolResult(
                success=False,
                message="No command provided.",
            )

        result = await self._service.execute(command)

        return ToolResult(
            success=result.success,
            message="Command executed." if result.success else "Command failed.",
            data={
                "command": result.command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            },
        )
