from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from dan.services.base import Service

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result of a shell command execution."""

    command: str
    stdout: str
    stderr: str
    returncode: int

    @property
    def success(self) -> bool:
        return self.returncode == 0


class ShellService(Service):
    """Executes shell commands on the Linux system.

    This service wraps asyncio subprocess execution and provides
    a clean interface for running shell commands.
    """

    name = "shell"

    def __init__(self, timeout: float = 30.0) -> None:
        self._timeout = timeout

    async def initialize(self) -> None:
        logger.debug("ShellService initialized")

    async def shutdown(self) -> None:
        logger.debug("ShellService shutdown")

    async def execute(
        self,
        command: str,
        timeout: float | None = None,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
    ) -> CommandResult:
        """Execute a shell command.

        Args:
            command: Shell command string to execute.
            timeout: Timeout in seconds. Uses instance default if None.
            cwd: Working directory for the command.
            env: Environment variables (merged with current env).

        Returns:
            CommandResult with stdout, stderr, and return code.
        """
        timeout = timeout or self._timeout

        logger.debug("Executing command: %s (timeout=%.1f)", command, timeout)

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=env,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )

            result = CommandResult(
                command=command,
                stdout=stdout.decode().strip(),
                stderr=stderr.decode().strip(),
                returncode=process.returncode or -1,
            )

            if result.success:
                logger.debug("Command succeeded: %s", command)
            else:
                logger.warning("Command failed (rc=%d): %s", result.returncode, command)

            return result

        except TimeoutError:
            logger.warning("Command timed out after %.1fs: %s", timeout, command)
            if process:
                process.kill()
                await process.communicate()
            return CommandResult(
                command=command,
                stdout="",
                stderr=f"Command timed out after {timeout}s",
                returncode=-1,
            )
        except Exception as e:
            logger.exception("Command execution failed: %s", command)
            return CommandResult(
                command=command,
                stdout="",
                stderr=str(e),
                returncode=-1,
            )
