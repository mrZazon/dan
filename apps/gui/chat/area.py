from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..theme.palette import Dark
from ..theme.typography import Font
from .widgets import (
    AssistantMessage,
    MessageGroup,
    StreamingCursor,
    ThinkingIndicator,
    ToolResultWidget,
    UserMessage,
)


class EmptyState(QWidget):
    """Centered home screen shown when there is no conversation."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        center = QWidget()
        center.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        layout = QVBoxLayout(center)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(0)

        layout.addStretch()

        pixmap = QPixmap("icon/icon-dark.png")
        logo = QLabel()
        logo.setPixmap(
            pixmap.scaled(
                128, 128,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(logo)

        subtitle = QLabel("Distributed Assistant Neural-network")
        subtitle.setFont(Font.mono(10))
        subtitle.setStyleSheet(f"color: {Dark.fg_3}; background: transparent; border: none;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(32)

        shortcuts = QWidget()
        sc_layout = QHBoxLayout(shortcuts)
        sc_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sc_layout.setSpacing(28)

        sc_data = [
            ("ctrl+n", "new chat"),
            ("ctrl+b", "s i d e b a r"),
            ("ctrl+i", "i n f o"),
            ("ctrl+,", "s e t t i n g s"),
        ]

        for key, desc in sc_data:
            block = QWidget()
            b_layout = QVBoxLayout(block)
            b_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            b_layout.setSpacing(4)

            k = QLabel(key)
            k.setFont(Font.mono(9))
            k.setStyleSheet(f"color: {Dark.thought}; background: transparent;")
            k.setAlignment(Qt.AlignmentFlag.AlignCenter)
            b_layout.addWidget(k)

            d = QLabel(desc)
            d.setFont(Font.mono(9))
            d.setStyleSheet(f"color: {Dark.fg_3}; background: transparent;")
            d.setAlignment(Qt.AlignmentFlag.AlignCenter)
            b_layout.addWidget(d)

            sc_layout.addWidget(block)

        layout.addWidget(shortcuts)

        layout.addSpacing(24)

        tip = QLabel("Type a message to begin")
        tip.setFont(Font.mono(10))
        tip.setStyleSheet(f"color: {Dark.fg_2}; background: transparent; border: none;")
        tip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tip)

        layout.addStretch()

        outer.addWidget(center)

    def reload_theme(self, mode: str) -> None:
        pass


class ChatArea(QWidget):
    """Conversation panel with empty state support.

    Shows a centered splash screen when empty.
    Switches to scrollable conversation when messages exist.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._thinking: ThinkingIndicator | None = None
        self._streaming: AssistantMessage | None = None
        self._cursor: StreamingCursor | None = None
        self._current_group: MessageGroup | None = None
        self._message_count = 0
        self._setup_ui()

    def _setup_ui(self) -> None:
        self._stack = QStackedWidget(self)

        self._empty = EmptyState()
        self._stack.addWidget(self._empty)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
            "QScrollArea > QWidget > QWidget { background: transparent; }"
        )

        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(14)
        self._layout.addStretch(1)

        self._scroll.setWidget(self._container)
        self._stack.addWidget(self._scroll)

        self._stack.setCurrentWidget(self._empty)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._stack)

    def begin_group(self) -> MessageGroup:
        group = MessageGroup()
        self._insert(group)
        self._current_group = group
        return group

    def add_user_message(self, text: str) -> None:
        self._switch_to_conversation()
        self._insert(UserMessage(text))
        self._message_count += 1

    def add_assistant_message(self, text: str) -> None:
        self._switch_to_conversation()
        self._message_count += 1
        if self._current_group:
            self._current_group.add_message(text)
        else:
            self._insert(AssistantMessage(text))

    def add_tool_result(self, tool_name: str, result: str) -> None:
        self._switch_to_conversation()
        self._insert(ToolResultWidget(tool_name, result))

    def show_thinking(self, status: str = "Thinking") -> None:
        self._switch_to_conversation()
        self._hide_thinking()
        self._thinking = ThinkingIndicator()
        self._thinking.set_status(status)
        self._insert(self._thinking)
        self._thinking.start()
        self._scroll_to_bottom()

    def update_thinking(self, status: str) -> None:
        if self._thinking:
            self._thinking.set_status(status)

    def hide_thinking(self) -> None:
        self._hide_thinking()

    def start_streaming(self) -> None:
        if self._thinking:
            self._thinking.fade_out(200)
            self._thinking = None
        QTimer.singleShot(200, self._begin_stream)

    def _begin_stream(self) -> None:
        self._streaming = AssistantMessage("")
        self._insert(self._streaming)
        self._cursor = StreamingCursor()
        self._layout.insertWidget(self._layout.count() - 1, self._cursor)
        self._scroll_to_bottom()

    def append_streaming_text(self, text: str) -> None:
        if self._streaming:
            self._streaming.append_text(text)
            self._scroll_to_bottom()

    def finish_streaming(self) -> None:
        if self._cursor:
            self._cursor.stop()
            self._layout.removeWidget(self._cursor)
            self._cursor.deleteLater()
            self._cursor = None
        self._streaming = None

    def reload_theme(self, mode: str) -> None:
        self._empty.reload_theme(mode)

    def clear(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._layout.addStretch(1)
        self._thinking = None
        self._streaming = None
        self._cursor = None
        self._current_group = None
        self._message_count = 0
        self._stack.setCurrentWidget(self._empty)

    def _switch_to_conversation(self) -> None:
        if self._stack.currentWidget() is self._empty:
            self._stack.setCurrentWidget(self._scroll)

    def _insert(self, widget: QWidget) -> None:
        self._switch_to_conversation()
        self._layout.insertWidget(self._layout.count() - 1, widget)
        self._scroll_to_bottom()

    def _hide_thinking(self) -> None:
        if self._thinking:
            self._thinking.stop()
            self._layout.removeWidget(self._thinking)
            self._thinking.deleteLater()
            self._thinking = None

    def _scroll_to_bottom(self) -> None:
        sb = self._scroll.verticalScrollBar()
        sb.setValue(sb.maximum())
