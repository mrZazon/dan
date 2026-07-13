from __future__ import annotations
from typing import Any
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool
from dan.services.shell import ShellService


@tool
class NetworkInterfacesTool(Tool):
    name = "network_interfaces"
    description = "Shows network interfaces"
    aliases = ("interfaces", "net interfaces")
    intents = {
        "network interfaces": 5,
        "show interfaces": 5,
        "network cards": 4,
        "ethernet": 3,
        "wifi": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("ip link show")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class IpAddrTool(Tool):
    name = "ip_addr"
    description = "Shows IP addresses"
    aliases = ("ip address", "my ip")
    intents = {
        "ip address": 5,
        "my ip": 5,
        "show ip": 5,
        "what is my ip": 4,
        "ip config": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("ip addr show")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class PingTool(Tool):
    name = "ping"
    description = "Pings a host"
    aliases = ("ping host", "check connection")
    intents = {
        "ping": 5,
        "can i reach": 4,
        "connection test": 3,
        "is host up": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        host = kwargs.get("host", "8.8.8.8")
        result = await self._service.execute(f"ping -c 4 {host}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class DnsLookupTool(Tool):
    name = "dns_lookup"
    description = "Performs DNS lookup"
    aliases = ("dns", "resolve")
    intents = {
        "dns lookup": 5,
        "resolve domain": 5,
        "dns query": 4,
        "ip for domain": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        domain = kwargs.get("domain", "example.com")
        result = await self._service.execute(f"nslookup {domain}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class NetstatTool(Tool):
    name = "netstat"
    description = "Shows network statistics"
    aliases = ("network stats", "connections")
    intents = {
        "network connections": 5,
        "open ports": 5,
        "netstat": 5,
        "network stats": 4,
        "listening ports": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("netstat -tuln")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class SsTool(Tool):
    name = "ss"
    description = "Shows socket statistics"
    aliases = ("socket stats", "ss stats")
    intents = {
        "socket stats": 5,
        "show sockets": 5,
        "ss command": 4,
        "network sockets": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("ss -tuln")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class TracerouteTool(Tool):
    name = "traceroute"
    description = "Traces route to host"
    aliases = ("trace route", "path to host")
    intents = {
        "traceroute": 5,
        "trace route": 5,
        "path to host": 4,
        "route to": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        host = kwargs.get("host", "8.8.8.8")
        result = await self._service.execute(f"traceroute {host}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class WgetCheckTool(Tool):
    name = "wget_check"
    description = "Checks if URL is reachable"
    aliases = ("check url", "url check")
    intents = {
        "check url": 5,
        "is url reachable": 5,
        "url status": 4,
        "can i reach url": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        url = kwargs.get("url", "http://example.com")
        result = await self._service.execute(f"wget --spider -q {url} && echo 'URL is reachable' || echo 'URL is not reachable'")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class HostLookupTool(Tool):
    name = "host_lookup"
    description = "Performs host lookup"
    aliases = ("host", "reverse dns")
    intents = {
        "host lookup": 5,
        "reverse dns": 5,
        "domain name": 4,
        "ip to domain": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        ip = kwargs.get("ip", "8.8.8.8")
        result = await self._service.execute(f"host {ip}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class CurlCheckTool(Tool):
    name = "curl_check"
    description = "Checks URL with curl"
    aliases = ("curl", "check site")
    intents = {
        "curl": 5,
        "check site": 5,
        "http headers": 4,
        "site status": 3,
    }

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        url = kwargs.get("url", "http://example.com")
        result = await self._service.execute(f"curl -I {url}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )
