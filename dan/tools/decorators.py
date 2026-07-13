from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dan.tools.base import Tool


def tool(cls: type[Tool]) -> type[Tool]:
    """
    Marks a Tool so it can be automatically discovered.
    """
    cls.__dan_tool__ = True
    return cls
