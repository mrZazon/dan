from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from ..theme.palette import PALETTE_MAP, Dark
from ..theme.typography import Font


class SidebarButton(QLabel):
    """Sidebar navigation item."""

    clicked = pyqtSignal()

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self._active = False
        self._palette = Dark
        self.setFont(Font.mono(11))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(30)
        self._apply_style()

    def _apply_style(self) -> None:
        p = self._palette
        if self._active:
            self.setStyleSheet(
                f"QLabel {{ color: {p.fg_0}; background: {p.bg_3}; "
                f"padding: 5px 14px; margin: 1px 8px; }}"
            )
        else:
            self.setStyleSheet(
                f"QLabel {{ color: {p.fg_3}; background: transparent; "
                f"padding: 5px 14px; margin: 1px 8px; }}"
                f"QLabel:hover {{ color: {p.fg_1}; background: {p.bg_2}; }}"
            )

    def reload_theme(self, mode: str) -> None:
        self._palette = PALETTE_MAP.get(mode, Dark)
        self._apply_style()

    def set_active(self, active: bool) -> None:
        self._active = active
        self._apply_style()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class Sidebar(QWidget):
    """Left sidebar with navigation, recent chats, and session info.

    Hidden by default. Shows with Ctrl+B.
    """

    new_chat_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    chat_selected = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._expanded = False
        self._buttons: list[SidebarButton] = []
        self._setup_ui()
        self.hide()
        self.setMinimumWidth(140)
        self.setMaximumWidth(220)
        self.resize(170, self.height())

    def _setup_ui(self) -> None:
        self.setStyleSheet(
            f"background: {Dark.bg_1}; border-right: 1px solid {Dark.border};"
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QLabel("D.A.N.")
        header.setFont(Font.mono(13))
        header.setStyleSheet(
            f"color: {Dark.fg_0}; padding: 14px 16px 10px 16px; border: none;"
        )
        root.addWidget(header)

        sep = QLabel("")
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {Dark.border}; margin: 0 14px;")
        root.addWidget(sep)

        root.addSpacing(6)

        btn = SidebarButton("+ New Chat")
        btn.clicked.connect(self.new_chat_clicked.emit)
        self._buttons.append(btn)
        root.addWidget(btn)

        root.addSpacing(8)

        recent_header = QLabel("Recent")
        recent_header.setFont(Font.mono(9))
        recent_header.setStyleSheet(
            f"color: {Dark.fg_3}; padding: 4px 16px 2px 16px; border: none;"
        )
        root.addWidget(recent_header)

        self._chat_list = QListWidget()
        self._chat_list.setFont(Font.mono(10))
        self._chat_list.setStyleSheet(
            f"""
            QListWidget {{
                background: transparent; border: none; outline: none;
                padding: 0 8px;
            }}
            QListWidget::item {{
                color: {Dark.fg_2};
                padding: 6px 8px;
                border: none;
            }}
            QListWidget::item:hover {{
                color: {Dark.fg_1};
                background: {Dark.bg_2};
            }}
            QListWidget::item:selected {{
                color: {Dark.fg_0};
                background: {Dark.bg_3};
            }}
        """
        )
        self._chat_list.currentRowChanged.connect(self._on_chat_selected)
        root.addWidget(self._chat_list, 1)

        self._info = QWidget()
        self._info.setStyleSheet("background: transparent;")
        info_layout = QVBoxLayout(self._info)
        info_layout.setContentsMargins(16, 8, 16, 12)
        info_layout.setSpacing(2)

        self._model_lbl = QLabel("dan-persona")
        self._model_lbl.setFont(Font.mono(9))
        self._model_lbl.setStyleSheet(f"color: {Dark.fg_3}; border: none;")
        info_layout.addWidget(self._model_lbl)

        self._conn_lbl = QLabel("Disconnected")
        self._conn_lbl.setFont(Font.mono(9))
        self._conn_lbl.setStyleSheet(f"color: {Dark.fg_3}; border: none;")
        info_layout.addWidget(self._conn_lbl)

        self._mem_lbl = QLabel("0 turns")
        self._mem_lbl.setFont(Font.mono(9))
        self._mem_lbl.setStyleSheet(f"color: {Dark.fg_3}; border: none;")
        info_layout.addWidget(self._mem_lbl)

        root.addWidget(self._info)

    def _on_chat_selected(self, row: int) -> None:
        if row >= 0:
            self.chat_selected.emit(row)

    def add_recent_chat(self, title: str) -> None:
        item = QListWidgetItem(title)
        self._chat_list.addItem(item)

    def clear_recent_chats(self) -> None:
        self._chat_list.clear()

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

    def set_model(self, name: str) -> None:
        self._model_lbl.setText(name)

    def set_connection(self, status: str) -> None:
        self._conn_lbl.setText(status)

    def set_memory(self, info: str) -> None:
        self._mem_lbl.setText(info)

    def reload_theme(self, mode: str) -> None:
        p = PALETTE_MAP.get(mode, Dark)
        self.setStyleSheet(
            f"background: {p.bg_1}; border-right: 1px solid {p.border};"
        )
        self._chat_list.setStyleSheet(
            f"""
            QListWidget {{
                background: transparent; border: none; outline: none;
                padding: 0 8px;
            }}
            QListWidget::item {{
                color: {p.fg_2};
                padding: 6px 8px;
                border: none;
            }}
            QListWidget::item:hover {{
                color: {p.fg_1};
                background: {p.bg_2};
            }}
            QListWidget::item:selected {{
                color: {p.fg_0};
                background: {p.bg_3};
            }}
        """
        )
        for btn in self._buttons:
            btn.reload_theme(mode)
