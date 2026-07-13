from __future__ import annotations
from typing import Any
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool
from dan.services.shell import ShellService


@tool
class ListFilesTool(Tool):
    name = "list_files"
    description = "Lists files in a directory"
    aliases = ("ls", "dir", "list")
    intents = {
        "list files": 5,
        "show files": 5,
        "ls": 5,
        "directory contents": 4,
        "what files": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", ".")
        result = await self._service.execute(f"ls -la {path}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class FileSizeTool(Tool):
    name = "dir_size"
    description = "Shows directory size using du"
    aliases = ("size", "du", "disk usage")
    intents = {
        "directory size": 5,
        "folder size": 5,
        "show directory size": 5,
        "how big is directory": 4,
        "disk usage": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", ".")
        result = await self._service.execute(f"du -sh {path}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class FileExistsTool(Tool):
    name = "fs_exists"
    description = "Checks if a file or directory exists"
    aliases = ("exists", "check file")
    intents = {
        "does file exist": 5,
        "is there a file": 4,
        "check path": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", "/etc/passwd")
        result = await self._service.execute(f"test -e {path} && echo 'EXISTS' || echo 'NOT FOUND'")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class FilePermissionsTool(Tool):
    name = "fs_permissions"
    description = "Shows file permissions in detail"
    aliases = ("permissions", "perms", "chmod info")
    intents = {
        "who can access": 4,
        "file access": 3,
        "access control": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", ".")
        result = await self._service.execute(f"ls -ld {path}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class FileOwnerTool(Tool):
    name = "file_owner"
    description = "Shows file owner"
    aliases = ("owner", "chown info")
    intents = {
        "file owner": 5,
        "who owns": 5,
        "show owner": 4,
        "chown": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", ".")
        result = await self._service.execute(f"stat -c '%U' {path}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class FileContentTool(Tool):
    name = "file_content"
    description = "Shows file content"
    aliases = ("cat", "read file")
    intents = {
        "file content": 5,
        "show file": 5,
        "read file": 5,
        "cat": 5,
        "file contents": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", "/etc/hostname")
        result = await self._service.execute(f"head -50 {path}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class FindFilesTool(Tool):
    name = "fs_find"
    description = "Finds files by name pattern"
    aliases = ("find", "search files")
    intents = {
        "locate file": 4,
        "where is file": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        name = kwargs.get("name", "*")
        path = kwargs.get("path", ".")
        result = await self._service.execute(f"find {path} -name '{name}' -type f 2>/dev/null | head -20")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class FileCountTool(Tool):
    name = "file_count"
    description = "Counts files in a directory"
    aliases = ("count files", "how many files")
    intents = {
        "count files": 5,
        "how many files": 5,
        "file count": 5,
        "number of files": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", ".")
        result = await self._service.execute(f"find {path} -type f | wc -l")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class DirectorySizeTool(Tool):
    name = "directory_size"
    description = "Shows directory sizes"
    aliases = ("dir size", "folder size")
    intents = {
        "directory size": 5,
        "folder size": 5,
        "show directory size": 5,
        "how big is directory": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", ".")
        result = await self._service.execute(f"du -sh {path}/* 2>/dev/null | sort -rh | head -10")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class RecentFilesTool(Tool):
    name = "recent_files"
    description = "Shows recently modified files"
    aliases = ("recent", "new files")
    intents = {
        "recent files": 5,
        "new files": 5,
        "modified files": 4,
        "latest files": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", ".")
        result = await self._service.execute(f"find {path} -type f -mtime -1 2>/dev/null | head -20")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )
