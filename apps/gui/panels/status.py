from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from ..animations.breathing import BreathingDot
from ..theme.palette import PALETTE_MAP, Dark
from ..theme.typography import Font


class StatusBar(QWidget):
    """Single-line status bar.

    Layout:  ● project   tokens   version   state
    Monospace, flat, minimal.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._items: dict[str, QLabel] = {}
        self._palette = Dark
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFixedHeight(22)
        self.setStyleSheet(
            f"""
            QWidget {{
                background: {Dark.bg_1};
                border-top: 1px solid {Dark.border};
            }}
        """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(0)

        self._dot = BreathingDot(self, Dark.success)
        self._dot.setFixedSize(8, 8)
        layout.addWidget(self._dot)
        layout.addSpacing(6)

        self._add_item(layout, "status", "Local")
        layout.addSpacing(6)

        self._add_item(layout, "version", "D.A.N. 0.1.0")

        layout.addStretch()

        self._add_item(layout, "tokens", "0 tokens")
        layout.addSpacing(16)
        self._add_item(layout, "state", "Idle")

    def _add_item(self, layout: QHBoxLayout, key: str, default: str) -> None:
        lbl = QLabel(default)
        lbl.setFont(Font.mono(9))
        lbl.setStyleSheet(f"color: {Dark.fg_2};")
        self._items[key] = lbl
        layout.addWidget(lbl)

    def set_value(self, key: str, value: str) -> None:
        if key in self._items:
            self._items[key].setText(value)

    def set_connected(self, connected: bool) -> None:
        if connected:
            self._dot.set_color(Dark.success)
            self.set_value("status", "Local")
        else:
            self._dot.set_color(Dark.error)
            self.set_value("status", "Offline")

    def start_pulse(self) -> None:
        self._dot.set_color(Dark.accent)
        self._dot.start()

    def stop_pulse(self) -> None:
        self._dot.stop()
        self._dot.set_color(Dark.success)

    def reload_theme(self, mode: str) -> None:
        p = PALETTE_MAP.get(mode, Dark)
        self._palette = p
        self.setStyleSheet(
            f"""
            QWidget {{
                background: {p.bg_1};
                border-top: 1px solid {p.border};
            }}
        """
        )
        for lbl in self._items.values():
            lbl.setStyleSheet(f"color: {p.fg_2};")
        if self._items.get("status", None):
            state = self._items["status"].text()
            color = p.success if state == "Local" else p.error
            self._dot.set_color(color)
