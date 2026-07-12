from __future__ import annotations

from typing import Type

from dan.tools.base import Tool


def tool(cls: Type[Tool]) -> Type[Tool]:
    """
    Marks a Tool so it can be automatically discovered.
    """
    cls.__dan_tool__ = True
    return cls