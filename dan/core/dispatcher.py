from dan.core.tool_registry import ToolRegistry

class Dispatcher:
    def __init__(self):
        self.registry = ToolRegistry()
        self.registry.discover()

    def dispatch(self, message: str) -> str:
        """
        Dispatch a message to the appropriate tool.
        """

        message = message.lower()

        for tool_class in self.registry._tool_classes.values():
            for alias in tool_class.aliases:
                if alias in message:
                    return tool_class.name

        return None