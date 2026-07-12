from __future__ import annotations

import importlib
import inspect
import pkgutil

import dan.tools

from dan.tools.base import Tool


class ToolRegistry:

    def __init__(self) -> None:
        self._tool_classes: dict[str, type[Tool]] = {}

    def discover(self) -> None:
        """
        Discover every tool inside dan.tools.
        """

        for _, module_name, _ in pkgutil.iter_modules(dan.tools.__path__):

            if module_name in ("base", "decorators"):
                continue

            module = importlib.import_module(f"dan.tools.{module_name}")

            for _, obj in inspect.getmembers(module, inspect.isclass):

                if not issubclass(obj, Tool):
                    continue

                if obj is Tool:
                    continue

                if not getattr(obj, "__dan_tool__", False):
                    continue

                self.register(obj)

    def register(self, tool_class: type[Tool]) -> None:

        instance = tool_class()

        if not instance.name:
            raise ValueError(
                f"{tool_class.__name__} has no name."
            )

        if instance.name in self._tool_classes:
            raise ValueError(
                f"Tool '{instance.name}' already registered."
            )

        self._tool_classes[instance.name] = tool_class

    def create(self, name: str) -> Tool:

        if name not in self._tool_classes:
            raise KeyError(name)

        return self._tool_classes[name]()

    async def execute(self, name: str, **kwargs):

        tool = self.create(name)

        return await tool.execute(**kwargs)

    def list(self) -> list[str]:
        return sorted(self._tool_classes.keys())