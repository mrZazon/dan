from __future__ import annotations

import enum

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor, QPalette


class ThemeMode(enum.Enum):
    DARK = "dark"
    LIGHT = "light"
    SYSTEM = "system"


class Dark:
    """Near-black monochrome palette. Developer-terminal aesthetic."""

    bg_0 = "#0a0a0a"
    bg_1 = "#101010"
    bg_2 = "#181818"
    bg_3 = "#222222"

    border = "#282828"
    border_light = "#333333"

    fg_0 = "#e8e8e8"
    fg_1 = "#aaaaaa"
    fg_2 = "#666666"
    fg_3 = "#444444"

    accent = "#7289c8"
    accent_light = "#8da0d8"
    accent_dark = "#5c72a8"

    thought = "#cc8855"
    thought_dim = "#a07040"

    success = "#7a9e7e"
    warning = "#b8a97a"
    error = "#c27070"

    @classmethod
    def make_palette(cls) -> QPalette:
        p = QPalette()
        p.setColor(QPalette.ColorRole.Window, QColor(cls.bg_0))
        p.setColor(QPalette.ColorRole.WindowText, QColor(cls.fg_0))
        p.setColor(QPalette.ColorRole.Base, QColor(cls.bg_1))
        p.setColor(QPalette.ColorRole.AlternateBase, QColor(cls.bg_0))
        p.setColor(QPalette.ColorRole.ToolTipBase, QColor(cls.bg_2))
        p.setColor(QPalette.ColorRole.ToolTipText, QColor(cls.fg_0))
        p.setColor(QPalette.ColorRole.Text, QColor(cls.fg_0))
        p.setColor(QPalette.ColorRole.Button, QColor(cls.bg_2))
        p.setColor(QPalette.ColorRole.ButtonText, QColor(cls.fg_0))
        p.setColor(QPalette.ColorRole.BrightText, QColor(cls.error))
        p.setColor(QPalette.ColorRole.Link, QColor(cls.accent))
        p.setColor(QPalette.ColorRole.Highlight, QColor(cls.accent))
        p.setColor(QPalette.ColorRole.HighlightedText, QColor(cls.bg_0))
        return p


class Light:
    """Light palette — white background, dark text, same accent."""

    bg_0 = "#f5f5f5"
    bg_1 = "#ffffff"
    bg_2 = "#e8e8e8"
    bg_3 = "#d0d0d0"

    border = "#cccccc"
    border_light = "#dddddd"

    fg_0 = "#1a1a1a"
    fg_1 = "#444444"
    fg_2 = "#888888"
    fg_3 = "#aaaaaa"

    accent = "#7289c8"
    accent_light = "#8da0d8"
    accent_dark = "#5c72a8"

    thought = "#aa6633"
    thought_dim = "#886644"

    success = "#4a7a4e"
    warning = "#8a7a3a"
    error = "#aa4040"

    @classmethod
    def make_palette(cls) -> QPalette:
        p = QPalette()
        p.setColor(QPalette.ColorRole.Window, QColor(cls.bg_0))
        p.setColor(QPalette.ColorRole.WindowText, QColor(cls.fg_0))
        p.setColor(QPalette.ColorRole.Base, QColor(cls.bg_1))
        p.setColor(QPalette.ColorRole.AlternateBase, QColor(cls.bg_0))
        p.setColor(QPalette.ColorRole.ToolTipBase, QColor(cls.bg_2))
        p.setColor(QPalette.ColorRole.ToolTipText, QColor(cls.fg_0))
        p.setColor(QPalette.ColorRole.Text, QColor(cls.fg_0))
        p.setColor(QPalette.ColorRole.Button, QColor(cls.bg_2))
        p.setColor(QPalette.ColorRole.ButtonText, QColor(cls.fg_0))
        p.setColor(QPalette.ColorRole.BrightText, QColor(cls.error))
        p.setColor(QPalette.ColorRole.Link, QColor(cls.accent))
        p.setColor(QPalette.ColorRole.Highlight, QColor(cls.accent))
        p.setColor(QPalette.ColorRole.HighlightedText, QColor(cls.bg_1))
        return p


PALETTE_MAP = {"dark": Dark, "light": Light}


class ThemeManager(QObject):
    theme_changed = pyqtSignal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._mode = ThemeMode.DARK
        self._accent = Dark.accent
        self._palette_class = Dark

    @property
    def mode(self) -> ThemeMode:
        return self._mode

    @property
    def accent(self) -> str:
        return self._accent

    @property
    def palette(self):
        return self._palette_class

    def _resolve_palette(self) -> None:
        self._palette_class = PALETTE_MAP.get(self._mode.value, Dark)

    def set_mode(self, mode: ThemeMode) -> None:
        self._mode = mode
        self._resolve_palette()
        self.theme_changed.emit(mode.value)

    def set_mode_from_string(self, name: str) -> None:
        try:
            self._mode = ThemeMode(name.lower())
        except ValueError:
            self._mode = ThemeMode.DARK
        self._resolve_palette()
        self.theme_changed.emit(self._mode.value)

    def set_accent(self, color: str) -> None:
        self._accent = color
        self._palette_class.accent = color
        self.theme_changed.emit(self._mode.value)

    def stylesheet(self) -> str:
        p = self._palette_class
        a = self._accent
        return f"""
QMainWindow, QDialog {{ background-color: {p.bg_0}; }}
QToolTip {{
    background: {p.bg_2}; color: {p.fg_1};
    border: 1px solid {p.border}; padding: 4px 7px; font-size: 11px;
}}
QScrollBar:vertical {{
    background: transparent; width: 4px; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {p.bg_3}; min-height: 30px; margin: 2px;
}}
QScrollBar::handle:vertical:hover {{ background: {p.fg_3}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ height: 0; }}
QMenuBar {{
    background: {p.bg_0}; border: none; padding: 2px 0;
    color: {p.fg_2};
}}
QMenuBar::item {{
    color: {p.fg_2}; padding: 4px 10px;
}}
QMenuBar::item:selected {{ background: {p.bg_2}; color: {p.fg_0}; }}
QMenu {{
    background: {p.bg_1}; border: 1px solid {p.border};
    padding: 3px;
}}
QMenu::item {{
    color: {p.fg_1}; padding: 4px 18px;
}}
QMenu::item:selected {{ background: {a}; color: {p.bg_0}; }}
QMenu::separator {{ height: 1px; background: {p.border}; margin: 3px 8px; }}
QStatusBar {{
    background: {p.bg_0}; border-top: 1px solid {p.border};
    color: {p.fg_3}; font-size: 10px; padding: 0px 10px;
}}
QStatusBar::item {{ border: none; }}
QPushButton {{
    background: {p.bg_2}; color: {p.fg_1};
    border: 1px solid {p.border};
    padding: 5px 14px; font-size: 12px;
}}
QPushButton:hover {{ border-color: {a}; color: {p.fg_0}; }}
QPushButton:pressed {{ background: {a}; color: {p.bg_0}; }}
QPushButton:disabled {{ background: {p.bg_1}; color: {p.fg_3}; border-color: {p.border}; }}
"""
