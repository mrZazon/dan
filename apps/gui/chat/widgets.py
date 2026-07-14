from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QTextCursor
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..animations.breathing import BreathingDot
from ..theme.palette import Dark
from ..theme.typography import Font


SPACING = 0


class StreamingCursor(QWidget):
    """Blinking block cursor: █"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._visible = True
        self.setFixedSize(9, 18)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._toggle)
        self._timer.start(500)

    def _toggle(self) -> None:
        self._visible = not self._visible
        self.update()

    def stop(self) -> None:
        self._timer.stop()
        self._visible = False
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        if not self._visible:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(Dark.accent))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 1, 8, 16)
        painter.end()


class ThinkingIndicator(QWidget):
    """Breathing dot + status text while model is thinking."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._opacity = 1.0
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._dot = BreathingDot(self, Dark.accent)
        self._dot.setFixedSize(10, 10)
        layout.addWidget(self._dot)

        self._label = QLabel("Thinking")
        self._label.setFont(Font.mono(11))
        self._label.setStyleSheet(
            f"color: {Dark.fg_3}; border: none; background: transparent;"
        )
        layout.addWidget(self._label)

        layout.addStretch()

    def set_status(self, text: str) -> None:
        self._label.setText(text)

    def start(self) -> None:
        self._dot.start()
        self._opacity = 1.0
        self.setWindowOpacity(1.0)
        self.show()

    def fade_out(self, duration: int = 200) -> None:
        self._anim = QPropertyAnimation(self, b"fadeOpacity")
        self._anim.setDuration(duration)
        self._anim.setStartValue(1.0)
        self._anim.setEndValue(0.0)
        self._anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self._anim.finished.connect(self._on_fade_done)
        self._dot.stop()
        self._anim.start()

    def _on_fade_done(self) -> None:
        self.hide()
        self._opacity = 1.0

    @pyqtProperty(float)
    def fadeOpacity(self) -> float:
        return self._opacity

    @fadeOpacity.setter
    def fadeOpacity(self, val: float) -> None:
        self._opacity = val
        self.setWindowOpacity(val)
        self.update()

    def stop(self) -> None:
        self._dot.stop()
        self.hide()


class FileAttachment(QWidget):
    """Compact file reference pill.

    [ File ] screenshot.png
    """

    def __init__(self, filename: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        tag = QLabel("File")
        tag.setFont(Font.mono(9))
        tag.setStyleSheet(
            f"color: {Dark.accent_light}; background: {Dark.accent_dark}; "
            f"padding: 1px 5px; border: none;"
        )
        layout.addWidget(tag)

        name = QLabel(filename)
        name.setFont(Font.mono(10))
        name.setStyleSheet(
            f"color: {Dark.fg_1}; background: transparent; border: none;"
        )
        layout.addWidget(name)

        layout.addStretch()


class ThoughtTiming(QWidget):
    """Thought timing metadata displayed before assistant responses.

    + Thought: 947ms
    """

    def __init__(self, elapsed_ms: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        text = f"+ Thought: {elapsed_ms}ms"
        lbl = QLabel(text)
        lbl.setFont(Font.mono(9))
        lbl.setStyleSheet(
            f"color: {Dark.thought}; background: transparent; border: none;"
        )
        layout.addWidget(lbl)
        layout.addStretch()


class ToolMetadata(QWidget):
    """Tool execution metadata displayed beneath responses.

    Build · DeepSeek V4 Flash Free · 4.9s
    """

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        lbl = QLabel(text)
        lbl.setFont(Font.mono(9))
        lbl.setStyleSheet(
            f"color: {Dark.fg_3}; background: transparent; border: none;"
        )
        layout.addWidget(lbl)
        layout.addStretch()


class UserMessage(QWidget):
    """Terminal-style user message.

    > install docker
    """

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, int(SPACING / 2), 0, int(SPACING / 2))
        layout.setSpacing(0)

        prompt = QLabel("  > ")
        prompt.setFont(Font.mono(13))
        prompt.setStyleSheet(
            f"color: {Dark.accent}; background: transparent; border: none;"
        )
        prompt.setFixedWidth(38)
        layout.addWidget(prompt)

        content = QLabel(text)
        content.setFont(Font.mono(13))
        content.setWordWrap(True)
        content.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        content.setStyleSheet(
            f"color: {Dark.fg_0}; background: transparent; border: none;"
        )
        layout.addWidget(content, 1)


class AssistantMessage(QWidget):
    """Plain text assistant response. No bubbles, no borders.

    Renders like terminal output. Includes thought timing
    and tool metadata sections.
    """

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._text = text
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, int(SPACING / 2), 0, int(SPACING / 2))
        layout.setSpacing(4)

        self._content = QTextEdit()
        self._content.setReadOnly(True)
        self._content.setPlainText(self._text)
        self._content.setFont(Font.mono(13))
        self._content.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._content.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._content.setFrameShape(QTextEdit.Shape.NoFrame)
        self._content.setStyleSheet(
            f"QTextEdit {{ color: {Dark.fg_0}; background: transparent; "
            f"border: none; padding: 0; "
            f"selection-background-color: {Dark.accent}; }}"
        )
        self._content.setMinimumHeight(16)
        self._content.document().setDocumentMargin(0)
        self._content.document().contentsChanged.connect(self._adjust_height)
        layout.addWidget(self._content)

        self._adjust_height()

    def _adjust_height(self) -> None:
        doc = self._content.document()
        doc.setTextWidth(self._content.viewport().width())
        h = int(doc.size().height())
        self._content.setFixedHeight(max(h, 16))

    def append_text(self, text: str) -> None:
        self._text += text
        cursor = self._content.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self._content.setTextCursor(cursor)
        self._content.ensureCursorVisible()
        self._adjust_height()

    def set_text(self, text: str) -> None:
        self._text = text
        self._content.setPlainText(text)
        self._adjust_height()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._adjust_height()


class MessageGroup(QWidget):
    """A complete assistant response group.

    Wraps optional FileAttachment(s) + optional ThoughtTiming
    + AssistantMessage + optional ToolMetadata into one
    vertically spaced block.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(4)
        self._message: AssistantMessage | None = None

    def add_file(self, filename: str) -> None:
        self._layout.addWidget(FileAttachment(filename))

    def add_thought(self, elapsed_ms: int) -> None:
        self._layout.addWidget(ThoughtTiming(elapsed_ms))

    def add_message(self, text: str) -> AssistantMessage:
        self._message = AssistantMessage(text)
        self._layout.addWidget(self._message)
        return self._message

    def add_metadata(self, text: str) -> None:
        self._layout.addWidget(ToolMetadata(text))

    @property
    def message(self) -> AssistantMessage | None:
        return self._message


class ToolResultWidget(QWidget):
    """Minimal tool output block."""

    def __init__(self, tool_name: str, result: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, int(SPACING / 2), 0, int(SPACING / 2))
        layout.setSpacing(2)

        header = QLabel(f"  [{tool_name}]")
        header.setFont(Font.mono(10))
        header.setStyleSheet(
            f"color: {Dark.accent}; background: transparent; border: none;"
        )
        layout.addWidget(header)

        if result:
            body = QLabel(result[:2000])
            body.setFont(Font.mono(10))
            body.setWordWrap(True)
            body.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            body.setStyleSheet(
                f"color: {Dark.fg_2}; background: {Dark.bg_2}; "
                f"padding: 6px 10px; border: none;"
            )
            layout.addWidget(body)
