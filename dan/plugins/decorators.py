from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dan.plugins.base import Plugin


def plugin(cls: type[Plugin]) -> type[Plugin]:
    cls.__dan_plugin__ = True
    return cls
