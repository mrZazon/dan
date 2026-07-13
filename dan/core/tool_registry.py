from __future__ import annotations

import importlib
import inspect
import logging
import pkgutil
from typing import TYPE_CHECKING

from dan.core.tool_match import ToolMatch
from dan.tools.base import Tool, ToolResult

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Discovers, registers, and manages tools.

    Tools are auto-discovered from the dan.tools package.
    Each tool must subclass Tool and be decorated with @tool.
    """

    def __init__(self) -> None:
        self._tool_classes: dict[str, type[Tool]] = {}

    def discover(self, packages: Sequence[str] | None = None) -> None:
        """Discover every tool in the given packages.

        Args:
            packages: Module paths to scan. Defaults to ["dan.tools"].
        """
        if packages is None:
            packages = ["dan.tools"]

        for pkg_path in packages:
            try:
                pkg = importlib.import_module(pkg_path)
            except ImportError:
                logger.warning("Cannot import package: %s", pkg_path)
                continue

            for _, module_name, _ in pkgutil.iter_modules(pkg.__path__):
                if module_name.startswith("_") or module_name in ("base", "decorators"):
                    continue

                try:
                    module = importlib.import_module(f"{pkg_path}.{module_name}")
                except ImportError:
                    logger.warning("Cannot import module: %s.%s", pkg_path, module_name)
                    continue

                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if not issubclass(obj, Tool) or obj is Tool:
                        continue
                    if not getattr(obj, "__dan_tool__", False):
                        continue
                    self.register(obj)

    def register(self, tool_class: type[Tool]) -> None:
        """Register a tool class.

        Raises:
            ValueError: If the tool has no name or name is already taken.
        """
        instance = tool_class()

        if not instance.name:
            raise ValueError(f"{tool_class.__name__} has no name.")

        if instance.name in self._tool_classes:
            raise ValueError(f"Tool '{instance.name}' already registered.")

        self._tool_classes[instance.name] = tool_class
        logger.debug("Registered tool: %s", instance.name)

    def get(self, name: str) -> type[Tool]:
        """Get a tool class by name."""
        if name not in self._tool_classes:
            raise KeyError(f"Unknown tool '{name}'")
        return self._tool_classes[name]

    def create(self, name: str) -> Tool:
        """Create a tool instance by name."""
        return self.get(name)()

    def match(self, message: str) -> ToolMatch | None:
        """Score all tools against a message and return the best match.

        Uses Tool.score() as the single source of scoring logic.
        Returns None if no tool scores above 0.
        """
        best_tool: type[Tool] | None = None
        best_score = 0.0

        for tool_class in self._tool_classes.values():
            score = tool_class.score(message)
            if score > best_score:
                best_score = score
                best_tool = tool_class

        if best_tool is None or best_score == 0.0:
            return None

        return ToolMatch(tool=best_tool, score=best_score)

    def tools(self) -> list[type[Tool]]:
        """Return every registered tool class."""
        return list(self._tool_classes.values())

    def names(self) -> list[str]:
        """Return sorted list of registered tool names."""
        return sorted(self._tool_classes.keys())

    async def execute(self, match: ToolMatch, **kwargs: object) -> ToolResult:
        """Execute a matched tool with the given arguments."""
        tool = match.tool()
        return await tool.execute(**kwargs)

    def __len__(self) -> int:
        return len(self._tool_classes)

    def __contains__(self, name: str) -> bool:
        return name in self._tool_classes
