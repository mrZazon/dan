from __future__ import annotations
from typing import Any
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool
from dan.services.shell import ShellService


@tool
class TarCreateTool(Tool):
    name = "tar_create"
    description = "Creates a tar archive"
    aliases = ("tar", "archive")
    intents = {
        "create archive": 5,
        "tar archive": 5,
        "compress to tar": 4,
        "make tar": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        source = kwargs.get("source", ".")
        dest = kwargs.get("dest", "archive.tar")
        result = await self._service.execute(f"tar -cf {dest} {source}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class TarExtractTool(Tool):
    name = "tar_extract"
    description = "Extracts a tar archive"
    aliases = ("untar", "extract")
    intents = {
        "extract archive": 5,
        "untar": 5,
        "extract tar": 5,
        "open tar": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        archive = kwargs.get("archive", "archive.tar")
        dest = kwargs.get("dest", ".")
        result = await self._service.execute(f"tar -xf {archive} -C {dest}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class GzipCompressTool(Tool):
    name = "gzip_compress"
    description = "Compresses a file with gzip"
    aliases = ("gzip", "compress")
    intents = {
        "gzip compress": 5,
        "compress file": 5,
        "gzip": 5,
        "make smaller": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        file = kwargs.get("file", "")
        result = await self._service.execute(f"gzip -k {file}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class GzipDecompressTool(Tool):
    name = "gzip_decompress"
    description = "Decompresses a gzip file"
    aliases = ("gunzip", "decompress")
    intents = {
        "gzip decompress": 5,
        "gunzip": 5,
        "decompress file": 5,
        "extract gzip": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        file = kwargs.get("file", "")
        result = await self._service.execute(f"gunzip -k {file}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class Bzip2CompressTool(Tool):
    name = "bzip2_compress"
    description = "Compresses a file with bzip2"
    aliases = ("bzip2", "bz2")
    intents = {
        "bzip2 compress": 5,
        "compress bzip2": 5,
        "bzip2": 5,
        "bz2 compress": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        file = kwargs.get("file", "")
        result = await self._service.execute(f"bzip2 -k {file}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class Bzip2DecompressTool(Tool):
    name = "bzip2_decompress"
    description = "Decompresses a bzip2 file"
    aliases = ("bunzip2", "bz2 decompress")
    intents = {
        "bzip2 decompress": 5,
        "bunzip2": 5,
        "decompress bzip2": 5,
        "extract bz2": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        file = kwargs.get("file", "")
        result = await self._service.execute(f"bunzip2 -k {file}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class XzCompressTool(Tool):
    name = "xz_compress"
    description = "Compresses a file with xz"
    aliases = ("xz", "lzma")
    intents = {
        "xz compress": 5,
        "compress xz": 5,
        "xz": 5,
        "lzma compress": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        file = kwargs.get("file", "")
        result = await self._service.execute(f"xz -k {file}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class XzDecompressTool(Tool):
    name = "xz_decompress"
    description = "Decompresses an xz file"
    aliases = ("unxz", "xz decompress")
    intents = {
        "xz decompress": 5,
        "unxz": 5,
        "decompress xz": 5,
        "extract xz": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        file = kwargs.get("file", "")
        result = await self._service.execute(f"unxz -k {file}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ZipCreateTool(Tool):
    name = "zip_create"
    description = "Creates a zip archive"
    aliases = ("zip", "create zip")
    intents = {
        "create zip": 5,
        "zip archive": 5,
        "compress to zip": 4,
        "make zip": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        source = kwargs.get("source", ".")
        dest = kwargs.get("dest", "archive.zip")
        result = await self._service.execute(f"zip -r {dest} {source}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ZipExtractTool(Tool):
    name = "zip_extract"
    description = "Extracts a zip archive"
    aliases = ("unzip", "extract zip")
    intents = {
        "extract zip": 5,
        "unzip": 5,
        "open zip": 4,
        "extract archive zip": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        archive = kwargs.get("archive", "archive.zip")
        dest = kwargs.get("dest", ".")
        result = await self._service.execute(f"unzip {archive} -d {dest}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )
