from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..theme.palette import PALETTE_MAP, Dark
from ..theme.typography import Font


class InfoRow(QWidget):
    """Key-value row in the info panel."""

    def __init__(self, key: str, value: str = "--", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = Dark
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 3, 16, 3)
        layout.setSpacing(0)

        self._key_lbl = QLabel(key)
        self._key_lbl.setFont(Font.mono(10))
        self._key_lbl.setStyleSheet(f"color: {Dark.fg_3}; background: transparent; border: none;")
        layout.addWidget(self._key_lbl)

        layout.addStretch()

        self._value = QLabel(value)
        self._value.setFont(Font.mono(10))
        self._value.setStyleSheet(f"color: {Dark.fg_1}; background: transparent; border: none;")
        layout.addWidget(self._value)

    def set_value(self, text: str) -> None:
        self._value.setText(text)

    def reload_theme(self, mode: str) -> None:
        p = PALETTE_MAP.get(mode, Dark)
        self._palette = p
        self._key_lbl.setStyleSheet(f"color: {p.fg_3}; background: transparent; border: none;")
        self._value.setStyleSheet(f"color: {p.fg_1}; background: transparent; border: none;")


class InfoSection(QWidget):
    """Named section containing info rows."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._rows: dict[str, InfoRow] = {}
        self._setup_ui(title)

    def _setup_ui(self, title: str) -> None:
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        lbl = QLabel(title)
        lbl.setFont(Font.mono(10))
        lbl.setStyleSheet(
            f"color: {Dark.fg_3}; background: transparent; border: none; "
            f"padding: 10px 16px 4px 16px;"
        )
        layout.addWidget(lbl)

    def add_row(self, key: str, default: str = "--") -> InfoRow:
        row = InfoRow(key, default)
        self._rows[key] = row
        self.layout().addWidget(row)  # type: ignore[union-attr]
        return row

    def set_value(self, key: str, value: str) -> None:
        if key in self._rows:
            self._rows[key].set_value(value)

    def reload_theme(self, mode: str) -> None:
        for row in self._rows.values():
            row.reload_theme(mode)


class Inspector(QWidget):
    """Collapsible right info panel.

    Shows session, context, backend, and performance info.
    Hidden by default. Toggles with Ctrl+I.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._expanded = False
        self._sections: dict[str, InfoSection] = {}
        self._setup_ui()
        self.hide()
        self.setMinimumWidth(180)
        self.setMaximumWidth(260)
        self.resize(220, self.height())

    def _setup_ui(self) -> None:
        self.setStyleSheet(
            f"background: {Dark.bg_1}; border-left: 1px solid {Dark.border};"
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QWidget()
        header.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 8, 8)
        header_layout.setSpacing(0)

        title = QLabel("Info")
        title.setFont(Font.mono(12))
        title.setStyleSheet(f"color: {Dark.fg_2}; background: transparent; border: none;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        close_btn = QPushButton("\u2715")
        close_btn.setFixedSize(22, 22)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(
            f"""
            QPushButton {{
                color: {Dark.fg_3}; background: transparent; border: none;
                font-size: 11px; padding: 0;
            }}
            QPushButton:hover {{ color: {Dark.fg_0}; background: {Dark.bg_2}; }}
        """
        )
        close_btn.clicked.connect(self.toggle)
        header_layout.addWidget(close_btn)

        root.addWidget(header)

        sep = QLabel("")
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {Dark.border};")
        root.addWidget(sep)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
            "QScrollArea > QWidget > QWidget { background: transparent; }"
        )

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        self._content_layout = QVBoxLayout(content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)

        self._build_sections()
        self._content_layout.addStretch()

        scroll.setWidget(content)
        root.addWidget(scroll, 1)

    def _build_sections(self) -> None:
        session = InfoSection("Session")
        session.add_row("Messages", "0")
        session.add_row("Turns", "0")
        self._sections["session"] = session
        self._content_layout.addWidget(session)

        ctx = InfoSection("Context")
        ctx.add_row("Tokens", "--")
        ctx.add_row("Usage", "--")
        self._sections["context"] = ctx
        self._content_layout.addWidget(ctx)

        backend = InfoSection("Backend")
        backend.add_row("Model", "dan-persona")
        backend.add_row("Provider", "--")
        backend.add_row("Connection", "Offline")
        self._sections["backend"] = backend
        self._content_layout.addWidget(backend)

        perf = InfoSection("Performance")
        perf.add_row("Latency", "--")
        perf.add_row("Gen time", "--")
        self._sections["performance"] = perf
        self._content_layout.addWidget(perf)

    @property
    def expanded(self) -> bool:
        return self._expanded

    def toggle(self) -> None:
        if self._expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self) -> None:
        self._expanded = True
        self.show()

    def collapse(self) -> None:
        self._expanded = False
        self.hide()

    def set_value(self, section: str, key: str, value: str) -> None:
        if section in self._sections:
            self._sections[section].set_value(key, value)

    def reload_theme(self, mode: str) -> None:
        p = PALETTE_MAP.get(mode, Dark)
        self.setStyleSheet(
            f"background: {p.bg_1}; border-left: 1px solid {p.border};"
        )
        for section in self._sections.values():
            section.reload_theme(mode)
