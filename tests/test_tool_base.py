from dan.core.tool_match import ToolMatch
from dan.tools.base import Tool, ToolResult


class MockTool(Tool):
    """A mock tool for testing."""

    name = "mock"
    description = "A mock tool."
    aliases = ("test", "mock")
    intents = {"test tool": 5, "mock tool": 4}

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(success=True, message="mock executed")


class EmptyTool(Tool):
    """A tool with no name."""

    name = ""
    description = "No name."

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(success=True)


class TestToolResult:
    def test_success(self):
        result = ToolResult(success=True, message="ok")
        assert result.success is True
        assert result.message == "ok"
        assert result.data is None
        assert result.metadata == {}

    def test_with_data(self):
        result = ToolResult(success=True, data={"key": "value"})
        assert result.data == {"key": "value"}


class TestTool:
    def test_score_exact_intent(self):
        assert MockTool.score("test tool") == 6.0  # 5 (intent) + 1 (alias "test")

    def test_score_alias(self):
        assert MockTool.score("please use the test") == 1.0

    def test_score_no_match(self):
        assert MockTool.score("hello world") == 0.0

    def test_score_case_insensitive(self):
        assert MockTool.score("TEST TOOL") == 6.0

    def test_score_multiple_matches(self):
        score = MockTool.score("test tool and mock tool")
        assert score == 11.0  # 5+4 (intents) + 1+1 (aliases)

    def test_score_alias_plus_intent(self):
        score = MockTool.score("test tool please")
        assert score == 6.0  # 1 (alias) + 5 (intent)


class TestToolMatch:
    def test_creation(self):
        match = ToolMatch(tool=MockTool, score=5.0)
        assert match.tool is MockTool
        assert match.score == 5.0

    def test_repr(self):
        match = ToolMatch(tool=MockTool, score=5.0)
        assert "mock" in repr(match)
        assert "5.0" in repr(match)
