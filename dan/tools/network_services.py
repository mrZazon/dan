from __future__ import annotations
from typing import Any
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool
from dan.services.shell import ShellService


@tool
class NmapTool(Tool):
    name = "nmap"
    description = "Scans ports with nmap"
    aliases = ("port scan", "network scan")
    intents = {
        "nmap": 5,
        "port scan": 5,
        "scan ports": 5,
        "open ports": 4,
        "network scan": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        host = kwargs.get("host", "localhost")
        result = await self._service.execute(f"nmap -sT {host}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class WgetDownloadTool(Tool):
    name = "wget_download"
    description = "Downloads a file with wget"
    aliases = ("wget", "download")
    intents = {
        "wget download": 5,
        "download file": 5,
        "wget": 5,
        "fetch url": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        url = kwargs.get("url", "http://example.com/file.txt")
        dest = kwargs.get("dest", ".")
        result = await self._service.execute(f"wget -P {dest} {url}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class CurlGetTool(Tool):
    name = "curl_get"
    description = "Fetches URL content with curl"
    aliases = ("curl", "fetch")
    intents = {
        "curl get": 5,
        "fetch url": 5,
        "curl": 5,
        "http get": 4,
        "download content": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        url = kwargs.get("url", "http://example.com")
        result = await self._service.execute(f"curl -s {url}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ScpTool(Tool):
    name = "scp"
    description = "Copies files with scp"
    aliases = ("secure copy", "remote copy")
    intents = {
        "scp": 5,
        "secure copy": 5,
        "remote copy": 5,
        "copy to server": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        source = kwargs.get("source", "")
        dest = kwargs.get("dest", "")
        result = await self._service.execute(f"scp {source} {dest}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class SshTool(Tool):
    name = "ssh"
    description = "Connects with SSH"
    aliases = ("secure shell", "remote login")
    intents = {
        "ssh": 5,
        "secure shell": 5,
        "remote login": 5,
        "connect to server": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        host = kwargs.get("host", "localhost")
        command = kwargs.get("command", "uptime")
        result = await self._service.execute(f"ssh {host} '{command}'")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class RsyncTool(Tool):
    name = "rsync"
    description = "Syncs files with rsync"
    aliases = ("sync", "remote sync")
    intents = {
        "rsync": 5,
        "sync files": 5,
        "remote sync": 5,
        "mirror directory": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        source = kwargs.get("source", "")
        dest = kwargs.get("dest", "")
        result = await self._service.execute(f"rsync -avz {source} {dest}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class NetCatTool(Tool):
    name = "netcat"
    description = "Tests connections with netcat"
    aliases = ("nc", "netcat")
    intents = {
        "netcat": 5,
        "nc": 5,
        "test port": 5,
        "check port": 4,
        "port test": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        host = kwargs.get("host", "localhost")
        port = kwargs.get("port", "80")
        result = await self._service.execute(f"nc -zv {host} {port}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class DigTool(Tool):
    name = "dig"
    description = "DNS lookup with dig"
    aliases = ("dns dig", "domain lookup")
    intents = {
        "dig": 5,
        "dns dig": 5,
        "domain lookup": 5,
        "dns query": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        domain = kwargs.get("domain", "example.com")
        result = await self._service.execute(f"dig {domain}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class HostnameResolveTool(Tool):
    name = "hostname_resolve"
    description = "Resolves hostname to IP"
    aliases = ("resolve host", "gethostbyname")
    intents = {
        "resolve hostname": 5,
        "hostname to ip": 5,
        "gethostbyname": 4,
        "dns resolve": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        hostname = kwargs.get("hostname", "example.com")
        result = await self._service.execute(f"getent hosts {hostname}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class WebSearchTool(Tool):
    name = "web_search"
    description = "Searches the internet via DuckDuckGo and returns results"
    aliases = ("search web", "internet search", "google")
    intents = {
        "search web": 5,
        "search internet": 5,
        "web search": 5,
        "search online": 5,
        "google": 4,
        "look up online": 4,
        "search for": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        query = kwargs.get("query", kwargs.get("message", ""))
        if not query:
            return ToolResult(success=False, message="No search query provided.")

        try:
            from ddgs import DDGS

            # Try news first for news-like queries
            news_keywords = {"news", "stock", "market", "finance", "weather", "score"}
            is_news = any(kw in query.lower() for kw in news_keywords)

            if is_news:
                results = DDGS().news(query, max_results=8)
            else:
                results = DDGS().text(query, max_results=8)

            if not results:
                return ToolResult(success=True, message=f"No results found for: {query}")

            lines: list[str] = []
            for i, r in enumerate(results, 1):
                title = r.get("title", "")
                url = r.get("url", r.get("href", r.get("link", "")))
                snippet = r.get("body", r.get("snippet", ""))
                entry = f"{i}. {title}\n   {url}"
                if snippet:
                    entry += f"\n   {snippet}"
                lines.append(entry)

            return ToolResult(
                success=True,
                message=f"Search results for: {query}\n\n" + "\n\n".join(lines),
            )
        except Exception as e:
            return ToolResult(success=False, message=f"Search failed: {e}")


@tool
class WebFetchTool(Tool):
    name = "web_fetch"
    description = "Fetches a URL and returns clean text content"
    aliases = ("fetch page", "read url", "scrape")
    intents = {
        "fetch page": 5,
        "read url": 5,
        "scrape": 5,
        "get page content": 5,
        "open url": 4,
        "read website": 4,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        import re as _re

        url = kwargs.get("url", "")
        if not url:
            return ToolResult(success=False, message="No URL provided.")

        cmd = (
            f"curl -s -L -A 'Mozilla/5.0' --max-time 15 "
            f"--max-filesize 1048576 '{url}'"
        )
        result = await self._service.execute(cmd)
        if not result.success:
            return ToolResult(success=False, message=result.stderr or "Failed to fetch URL.")

        html = result.stdout
        # Strip script/style tags
        html = _re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
        # Strip HTML tags
        text = _re.sub(r"<[^>]+>", " ", html)
        # Collapse whitespace
        text = _re.sub(r"\s+", " ", text).strip()
        # Limit output
        if len(text) > 4000:
            text = text[:4000] + "\n... (truncated)"

        if not text:
            return ToolResult(success=True, message="Page returned empty content.")

        return ToolResult(
            success=True,
            message=f"Content from {url}:\n\n{text}",
        )


@tool
class CWhoisTool(Tool):
    name = "whois"
    description = "Looks up domain whois"
    aliases = ("domain whois", "register info")
    intents = {
        "whois": 5,
        "domain whois": 5,
        "register info": 5,
        "domain info": 4,
        "owner of domain": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        domain = kwargs.get("domain", "example.com")
        result = await self._service.execute(f"whois {domain}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )
