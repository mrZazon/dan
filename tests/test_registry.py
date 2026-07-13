import pytest

from dan.core.tool_registry import ToolRegistry
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool


@tool
class AlphaTool(Tool):
    name = "alpha"
    description = "Alpha tool."
    aliases = ("alpha",)
    intents = {"do alpha": 5}

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(success=True, message="alpha")


@tool
class BetaTool(Tool):
    name = "beta"
    description = "Beta tool."
    aliases = ("beta",)
    intents = {"do beta": 5}

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(success=True, message="beta")


class TestToolRegistry:
    def test_discover_finds_tools(self):
        registry = ToolRegistry()
        registry.discover()
        names = registry.names()
        assert "command" in names
        assert "echo" in names
        assert "hour" in names

    def test_register_custom_tool(self):
        registry = ToolRegistry()
        registry.register(AlphaTool)
        assert "alpha" in registry
        assert len(registry) == 1

    def test_register_duplicate_raises(self):
        registry = ToolRegistry()
        registry.register(AlphaTool)
        with pytest.raises(ValueError, match="already registered"):
            registry.register(AlphaTool)

    def test_create_tool(self):
        registry = ToolRegistry()
        registry.register(AlphaTool)
        instance = registry.create("alpha")
        assert isinstance(instance, AlphaTool)

    def test_create_unknown_raises(self):
        registry = ToolRegistry()
        with pytest.raises(KeyError, match="Unknown tool"):
            registry.create("nonexistent")

    def test_match_returns_best(self):
        registry = ToolRegistry()
        registry.register(AlphaTool)
        registry.register(BetaTool)
        match = registry.match("do alpha")
        assert match is not None
        assert match.tool is AlphaTool
        assert match.score == 6.0  # 5 (intent) + 1 (alias)

    def test_match_returns_none_on_no_score(self):
        registry = ToolRegistry()
        registry.register(AlphaTool)
        match = registry.match("hello world")
        assert match is None

    def test_list_sorted(self):
        registry = ToolRegistry()
        registry.register(BetaTool)
        registry.register(AlphaTool)
        assert registry.names() == ["alpha", "beta"]
