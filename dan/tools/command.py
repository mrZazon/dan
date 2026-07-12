import asyncio

from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool


@tool
class CommandTool(Tool):
    """
    Execute a single shell command.

    This tool is stateless. It creates a new shell process for each execution.
    """

    name = "command"

    description = "Execute a shell command."

    aliases = (
        "command",
        "shell",
        "bash",
        "terminal",
    )

    async def execute(self, **kwargs) -> ToolResult:

        command = kwargs.get("command")

        if not command:
            return ToolResult(
                success=False,
                message="No command provided.",
            )

        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        return ToolResult(
            success=process.returncode == 0,
            message="Command executed.",
            data={
                "command": command,
                "stdout": stdout.decode().strip(),
                "stderr": stderr.decode().strip(),
                "returncode": process.returncode,
            },
        )