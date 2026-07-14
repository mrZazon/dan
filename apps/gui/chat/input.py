from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent, QPainter, QColor
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..theme.palette import PALETTE_MAP, Dark
from ..theme.typography import Font


class InputEditor(QPlainTextEdit):
    """Editor-style input field with placeholder text.

    Feels like typing in a terminal or code editor.
    Shows placeholder when empty and unfocused.
    """

    submit = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._placeholder = "Ask anything..."
        self._has_placeholder = True
        self.setFont(Font.mono(13))
        self.setTabChangesFocus(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMaximumBlockCount(12)
        self.setFixedHeight(44)
        self.setStyleSheet(
            f"""
            QPlainTextEdit {{
                color: {Dark.fg_0};
                background: transparent;
                border: none;
                padding: 10px 0px 8px 0px;
                selection-background-color: {Dark.accent};
            }}
        """
        )
        self.show_placeholder()

    def show_placeholder(self) -> None:
        if not self.toPlainText():
            self._has_placeholder = True
            self.setPlainText(self._placeholder)
            self.selectAll()

    def hide_placeholder(self) -> None:
        if self._has_placeholder:
            self._has_placeholder = False
            self.setPlainText("")

    def focusInEvent(self, event) -> None:  # noqa: N802
        self.hide_placeholder()
        super().focusInEvent(event)
        self.selectAll()

    def focusOutEvent(self, event) -> None:  # noqa: N802
        super().focusOutEvent(event)
        self.show_placeholder()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                super().keyPressEvent(event)
            else:
                self.submit.emit()
        elif (
            event.key() == Qt.Key.Key_L
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            self.clear()
        else:
            super().keyPressEvent(event)

    def toPlainText(self) -> str:  # noqa: N802
        text = super().toPlainText()
        if self._has_placeholder and text == self._placeholder:
            return ""
        return text

    def minimumSizeHint(self):  # noqa: N802
        from PyQt6.QtCore import QSize
        return QSize(200, 44)


class InputArea(QWidget):
    """Bottom input area with blue left accent border.

    ├ Ask anything...
    └ Build · dan-persona
    """

    message_submitted = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = Dark
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFixedHeight(86)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._container = QWidget()
        self._container.setStyleSheet(
            f"background: {Dark.bg_1}; border: none;"
        )

        inner = QVBoxLayout(self._container)
        inner.setContentsMargins(0, 0, 0, 0)
        inner.setSpacing(0)

        editor_row = QWidget()
        editor_row.setStyleSheet("background: transparent;")
        er_layout = QHBoxLayout(editor_row)
        er_layout.setContentsMargins(0, 0, 0, 0)
        er_layout.setSpacing(0)

        self._accent_border = AccentBorder()
        self._accent_border.setFixedWidth(3)
        er_layout.addWidget(self._accent_border)

        self._editor = InputEditor()
        self._editor.submit.connect(self._on_submit)
        er_layout.addWidget(self._editor, 1)

        inner.addWidget(editor_row)

        self._sep = QLabel("")
        self._sep.setFixedHeight(1)
        self._sep.setStyleSheet(f"background: {Dark.border};")
        inner.addWidget(self._sep)

        footer = QWidget()
        footer.setStyleSheet("background: transparent;")
        footer.setFixedHeight(20)
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(16, 0, 16, 0)
        f_layout.setSpacing(0)

        self._model_info = QLabel("Build \u00b7 dan-persona")
        self._model_info.setFont(Font.mono(9))
        self._model_info.setStyleSheet(
            f"color: {Dark.fg_3}; background: transparent; border: none;"
        )
        f_layout.addWidget(self._model_info)
        f_layout.addStretch()

        inner.addWidget(footer)

        outer.addWidget(self._container)

    def _on_submit(self) -> None:
        text = self._editor.toPlainText()
        if text:
            self._editor.clear()
            self.message_submitted.emit(text)

    def set_enabled(self, enabled: bool) -> None:
        self._editor.setReadOnly(not enabled)

    def focus_input(self) -> None:
        self._editor.setFocus()

    def set_model(self, name: str) -> None:
        self._model_info.setText(f"Build \u00b7 {name}")

    def set_accent(self, color: str) -> None:
        self._accent_border.set_accent(color)

    def reload_theme(self, mode: str) -> None:
        p = PALETTE_MAP.get(mode, Dark)
        self._palette = p
        self._container.setStyleSheet(
            f"background: {p.bg_1}; border: none;"
        )
        self._sep.setStyleSheet(f"background: {p.border};")
        self._model_info.setStyleSheet(
            f"color: {p.fg_3}; background: transparent; border: none;"
        )
        self._accent_border.set_accent(p.accent)


class AccentBorder(QWidget):
    """Thin vertical accent bar drawn on the input left edge."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color = Dark.accent

    def set_accent(self, color: str) -> None:
        self._color = color
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(self._color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, 3, self.height())
        painter.end()
