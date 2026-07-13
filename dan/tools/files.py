from __future__ import annotations
from typing import Any
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool
from dan.services.shell import ShellService


@tool
class ListDirTool(Tool):
    name = "list_dir"
    description = "Lists directory contents"
    aliases = ("ls", "list")
    intents = {"list files": 5, "list directory": 5, "show files": 4, "dir contents": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", ".")
        result = await self._service.execute(f"ls -la {path}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class ReadFileTool(Tool):
    name = "read_file"
    description = "Reads file contents"
    aliases = ("cat", "read")
    intents = {"read file": 5, "show file": 4, "view file": 4, "cat file": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        result = await self._service.execute(f"cat {path}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class WriteFileTool(Tool):
    name = "write_file"
    description = "Writes content to a file"
    aliases = ("write", "create file")
    intents = {"write file": 5, "create file": 4, "save file": 4, "overwrite file": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        content = kwargs.get("content")
        result = await self._service.execute(f'echo "{content}" > {path}')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class AppendFileTool(Tool):
    name = "append_file"
    description = "Appends content to a file"
    aliases = ("append",)
    intents = {"append to file": 5, "add to file": 4, "append file": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        content = kwargs.get("content")
        result = await self._service.execute(f'echo "{content}" >> {path}')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class CopyFileTool(Tool):
    name = "copy_file"
    description = "Copies a file"
    aliases = ("cp", "copy")
    intents = {"copy file": 5, "duplicate file": 4, "copy to": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        source = kwargs.get("source")
        destination = kwargs.get("destination")
        result = await self._service.execute(f"cp {source} {destination}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class MoveFileTool(Tool):
    name = "move_file"
    description = "Moves or renames a file"
    aliases = ("mv", "move", "rename")
    intents = {"move file": 5, "rename file": 5, "move to": 4, "rename to": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        source = kwargs.get("source")
        destination = kwargs.get("destination")
        result = await self._service.execute(f"mv {source} {destination}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class DeleteFileTool(Tool):
    name = "delete_file"
    description = "Deletes a file"
    aliases = ("rm", "delete", "remove")
    intents = {"delete file": 5, "remove file": 5, "rm file": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        result = await self._service.execute(f"rm -f {path}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class MkdirTool(Tool):
    name = "mkdir"
    description = "Creates a directory"
    aliases = ("mkdir", "create directory")
    intents = {"create directory": 5, "make directory": 5, "create folder": 4, "make folder": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        result = await self._service.execute(f"mkdir -p {path}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class RmdirTool(Tool):
    name = "rmdir"
    description = "Removes a directory and its contents"
    aliases = ("rmdir", "remove directory")
    intents = {"remove directory": 5, "delete directory": 5, "remove folder": 4, "delete folder": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        result = await self._service.execute(f"rm -rf {path}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class FileExistsTool(Tool):
    name = "file_exists"
    description = "Checks if a file exists"
    aliases = ("exists",)
    intents = {"check if file exists": 5, "file exists": 4, "does file exist": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        result = await self._service.execute(f'test -f {path} && echo "exists" || echo "not found"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class FileSizeTool(Tool):
    name = "file_size"
    description = "Shows file size"
    aliases = ("size", "fsize")
    intents = {"file size": 5, "how big is": 4, "show size": 4, "file size info": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        result = await self._service.execute(f"ls -lh {path}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class FilePermsTool(Tool):
    name = "file_permissions"
    description = "Shows file permissions"
    aliases = ("perms", "stat")
    intents = {"file permissions": 5, "show permissions": 4, "file ownership": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        result = await self._service.execute(f'stat -c "%A %a %U %G" {path}')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class ChmodTool(Tool):
    name = "chmod"
    description = "Changes file permissions"
    aliases = ("chmod", "set permissions")
    intents = {"change permissions": 5, "set permissions": 5, "chmod file": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        mode = kwargs.get("mode", "755")
        result = await self._service.execute(f"chmod {mode} {path}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class FindFilesTool(Tool):
    name = "find_files"
    description = "Finds files by name"
    aliases = ("find", "search files")
    intents = {"find files": 5, "search files": 5, "locate file": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", ".")
        name = kwargs.get("name")
        result = await self._service.execute(f'find {path} -name "{name}" -type f 2>/dev/null | head -20')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class FileHeadTool(Tool):
    name = "file_head"
    description = "Shows first lines of a file"
    aliases = ("head",)
    intents = {"show first lines": 5, "head of file": 4, "beginning of file": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        lines = kwargs.get("lines", "10")
        result = await self._service.execute(f"head -n {lines} {path}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class FileTailTool(Tool):
    name = "file_tail"
    description = "Shows last lines of a file"
    aliases = ("tail",)
    intents = {"show last lines": 5, "tail of file": 4, "end of file": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        lines = kwargs.get("lines", "10")
        result = await self._service.execute(f"tail -n {lines} {path}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class WcTool(Tool):
    name = "word_count"
    description = "Counts words, lines, and characters in a file"
    aliases = ("wc", "count")
    intents = {"count words": 5, "word count": 5, "count lines": 4, "file statistics": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        result = await self._service.execute(f"wc {path}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class Md5SumTool(Tool):
    name = "md5"
    description = "Computes MD5 hash of a file"
    aliases = ("md5", "md5sum")
    intents = {"md5 hash": 5, "compute md5": 5, "md5sum": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        result = await self._service.execute(f"md5sum {path}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class Sha256Tool(Tool):
    name = "sha256"
    description = "Computes SHA256 hash of a file"
    aliases = ("sha256", "sha256sum")
    intents = {"sha256 hash": 5, "compute sha256": 5, "sha256sum": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        result = await self._service.execute(f"sha256sum {path}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class TarTool(Tool):
    name = "tar"
    description = "Creates a tar.gz archive"
    aliases = ("tar", "archive", "compress")
    intents = {"create archive": 5, "tar archive": 5, "compress file": 4, "create tar": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        archive = kwargs.get("archive")
        source = kwargs.get("source")
        result = await self._service.execute(f"tar czf {archive} {source}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})
