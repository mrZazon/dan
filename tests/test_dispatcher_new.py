from dan.core.dispatcher import Dispatcher, DispatchResult


class TestDispatcher:
    def test_dispatch_matching_tool(self):
        dispatcher = Dispatcher()
        result = dispatcher.dispatch("what time is it")
        assert result.match is not None
        assert result.match.tool.name in ("hour", "current_time")
        assert result.confidence > 0

    def test_dispatch_no_match(self):
        dispatcher = Dispatcher()
        result = dispatcher.dispatch("hello world foo bar")
        assert result.match is None

    def test_dispatch_threshold(self):
        dispatcher = Dispatcher(threshold=100.0)
        result = dispatcher.dispatch("what time is it")
        assert result.match is None
        assert result.confidence > 0

    def test_dispatch_returns_dispatch_result(self):
        dispatcher = Dispatcher()
        result = dispatcher.dispatch("run command ls")
        assert isinstance(result, DispatchResult)
        assert result.match is not None
        assert result.match.tool.name == "command"

    def test_dispatch_case_insensitive(self):
        dispatcher = Dispatcher()
        result = dispatcher.dispatch("WHAT TIME IS IT")
        assert result.match is not None
        assert result.match.tool.name in ("hour", "current_time")

    def test_dispatch_command_tool(self):
        dispatcher = Dispatcher()
        result = dispatcher.dispatch("execute command ls -la")
        assert result.match is not None
        assert result.match.tool.name == "command"
        assert result.confidence >= 5.0
