from __future__ import annotations
from typing import Any
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool
from dan.services.shell import ShellService


@tool
class CalculatorTool(Tool):
    name = "calculator"
    description = "Evaluates a mathematical expression"
    aliases = ("calc", "math")
    intents = {"calculate": 5, "math": 4, "calculator": 5, "compute": 4, "evaluate": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        expression = kwargs.get("expression", "")
        result = await self._service.execute(f'python3 -c "print({expression})"')
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class Base64EncodeTool(Tool):
    name = "base64_encode"
    description = "Encodes text to base64"
    aliases = ("b64encode",)
    intents = {"base64 encode": 5, "encode base64": 5, "base64": 3, "b64 encode": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        result = await self._service.execute(f'echo -n "{text}" | base64')
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class Base64DecodeTool(Tool):
    name = "base64_decode"
    description = "Decodes base64 encoded text"
    aliases = ("b64decode",)
    intents = {"base64 decode": 5, "decode base64": 5, "b64 decode": 4, "unbase64": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        result = await self._service.execute(f'echo "{text}" | base64 -d')
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class UrlEncodeTool(Tool):
    name = "url_encode"
    description = "URL encodes text"
    aliases = ("urlencode",)
    intents = {"url encode": 5, "encode url": 5, "urlencode": 4, "percent encode": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        result = await self._service.execute(f"python3 -c \"import urllib.parse; print(urllib.parse.quote('{text}'))\"")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class UrlDecodeTool(Tool):
    name = "url_decode"
    description = "URL decodes text"
    aliases = ("urldecode",)
    intents = {"url decode": 5, "decode url": 5, "urldecode": 4, "percent decode": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        result = await self._service.execute(f"python3 -c \"import urllib.parse; print(urllib.parse.unquote('{text}'))\"")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class JsonFormatTool(Tool):
    name = "json_format"
    description = "Formats and pretty-prints JSON text"
    aliases = ("json_pretty", "pretty_json")
    intents = {"format json": 5, "pretty json": 5, "json format": 4, "json pretty print": 5, "beautify json": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        result = await self._service.execute(f"echo '{text}' | python3 -m json.tool")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class JsonValidateTool(Tool):
    name = "json_validate"
    description = "Validates whether text is valid JSON"
    aliases = ("check_json",)
    intents = {"validate json": 5, "json validate": 5, "check json": 4, "is valid json": 4, "json valid": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        result = await self._service.execute(
            f"echo '{text}' | python3 -m json.tool > /dev/null 2>&1 && echo \"Valid JSON\" || echo \"Invalid JSON\""
        )
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class UuidGenTool(Tool):
    name = "uuid_gen"
    description = "Generates a random UUID v4"
    aliases = ("uuid", "generate_uuid")
    intents = {"generate uuid": 5, "uuid generate": 5, "uuid": 4, "random uuid": 5, "create uuid": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("cat /proc/sys/kernel/random/uuid")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class HashTextTool(Tool):
    name = "hash_text"
    description = "Hashes text with MD5"
    aliases = ("md5", "md5hash")
    intents = {"hash text": 4, "md5 hash": 5, "md5": 5, "md5sum": 5, "hash md5": 4, "text hash": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        result = await self._service.execute(f'echo -n "{text}" | md5sum | cut -d\' \' -f1')
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class Sha256TextTool(Tool):
    name = "sha256_text"
    description = "Hashes text with SHA256"
    aliases = ("sha256", "sha256hash")
    intents = {"sha256 hash": 5, "sha256": 5, "sha256sum": 5, "hash sha256": 4, "text sha256": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        result = await self._service.execute(f'echo -n "{text}" | sha256sum | cut -d\' \' -f1')
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class WordCountTool(Tool):
    name = "text_word_count"
    description = "Counts the number of words in text"
    aliases = ("wc", "wordcount")
    intents = {"count words": 5, "word count": 5, "how many words": 5, "text word count": 4, "wc": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        result = await self._service.execute(f'echo "{text}" | wc -w')
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class CharCountTool(Tool):
    name = "text_char_count"
    description = "Counts the number of characters in text"
    aliases = ("charcount",)
    intents = {"count characters": 5, "character count": 5, "how many characters": 5, "char count": 4, "text char count": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        result = await self._service.execute(f'echo -n "{text}" | wc -c')
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class TextToUpperTool(Tool):
    name = "text_to_upper"
    description = "Converts text to uppercase"
    aliases = ("upper", "toupper")
    intents = {"uppercase": 5, "to upper": 5, "convert to upper": 4, "text to upper": 4, "make uppercase": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        result = await self._service.execute(f'echo "{text}" | tr \'[:lower:]\' \'[:upper:]\'')
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class TextToLowerTool(Tool):
    name = "text_to_lower"
    description = "Converts text to lowercase"
    aliases = ("lower", "tolower")
    intents = {"lowercase": 5, "to lower": 5, "convert to lower": 4, "text to lower": 4, "make lowercase": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        result = await self._service.execute(f'echo "{text}" | tr \'[:upper:]\' \'[:lower:]\'')
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class TextReverseTool(Tool):
    name = "text_reverse"
    description = "Reverses the given text"
    aliases = ("reverse",)
    intents = {"reverse text": 5, "text reverse": 5, "reverse string": 5, "flip text": 4, "backward text": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        result = await self._service.execute(f'echo "{text}" | rev')
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class SortTextTool(Tool):
    name = "sort_text"
    description = "Sorts lines of text alphabetically"
    aliases = ("sort",)
    intents = {"sort lines": 5, "sort text": 5, "alphabetical sort": 5, "sort alphabetically": 5, "text sort": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        result = await self._service.execute(f'echo "{text}" | sort')
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class UniqueLinesTool(Tool):
    name = "unique_lines"
    description = "Removes duplicate lines from text"
    aliases = ("dedup", "deduplicate")
    intents = {"remove duplicates": 5, "unique lines": 5, "deduplicate": 5, "dedup lines": 4, "remove duplicate lines": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        result = await self._service.execute(f'echo "{text}" | sort -u')
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class GrepTextTool(Tool):
    name = "grep_text"
    description = "Searches text for lines matching a pattern"
    aliases = ("grep", "search")
    intents = {"search text": 5, "grep text": 5, "find in text": 4, "text grep": 4, "pattern match": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        pattern = kwargs.get("pattern", "")
        result = await self._service.execute(f'echo "{text}" | grep "{pattern}"')
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ReplaceTextTool(Tool):
    name = "replace_text"
    description = "Replaces occurrences of a substring in text"
    aliases = ("replace", "sed")
    intents = {"replace text": 5, "text replace": 5, "find and replace": 5, "substitute text": 4, "text substitute": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        old = kwargs.get("old", "")
        new = kwargs.get("new", "")
        result = await self._service.execute(f'echo "{text}" | sed "s/{old}/{new}/g"')
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class TrimTextTool(Tool):
    name = "trim_text"
    description = "Trims leading and trailing whitespace from text"
    aliases = ("trim",)
    intents = {"trim whitespace": 5, "trim text": 5, "strip whitespace": 5, "remove whitespace": 4, "text trim": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        result = await self._service.execute(f'echo "{text}" | xargs')
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )
