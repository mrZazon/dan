from __future__ import annotations

from PyQt6.QtGui import QFont


class Font:
    """Monospace font throughout.

    Uses Qt's built-in fallback chain: tries each family
    in order until one is found on the system.
    """

    _families = "JetBrains Mono, IBM Plex Mono, Hack, DejaVu Sans Mono, monospace"

    @staticmethod
    def ui(size: int = 13) -> QFont:
        f = QFont(Font._families, size)
        f.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        return f

    @staticmethod
    def mono(size: int = 13) -> QFont:
        f = QFont(Font._families, size)
        f.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        return f

    @staticmethod
    def ui_family() -> str:
        return Font._families

    @staticmethod
    def mono_family() -> str:
        return Font._families
