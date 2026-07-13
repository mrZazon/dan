from __future__ import annotations

import time

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

BUBBLE_STYLES = {
    "user": {
        "header": "#64d2ff",
        "bg": "rgba(100, 210, 255, 20)",
        "align": Qt.AlignmentFlag.AlignRight,
    },
    "assistant": {
        "header": "#30d158",
        "bg": "rgba(48, 209, 88, 12)",
        "align": Qt.AlignmentFlag.AlignLeft,
    },
    "tool": {
        "header": "#ffd60a",
        "bg": "rgba(255, 214, 10, 12)",
        "align": Qt.AlignmentFlag.AlignLeft,
    },
    "error": {
        "header": "#ff453a",
        "bg": "rgba(255, 69, 58, 15)",
        "align": Qt.AlignmentFlag.AlignLeft,
    },
}


class MessageBubble(QWidget):
    def __init__(
        self, role: str, content: str,
        timestamp: float | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        ts = timestamp or time.time()
        time_str = time.strftime("%I:%M %p", time.localtime(ts))

        style = BUBBLE_STYLES.get(role, BUBBLE_STYLES["error"])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 6, 16, 6)
        layout.setSpacing(3)
        layout.setAlignment(style["align"])

        header = QLabel(f"{'You' if role == 'user' else role.capitalize()} &middot; {time_str}")
        header.setTextFormat(Qt.TextFormat.RichText)
        header.setStyleSheet(
            f"color: {style['header']}; font-size: 11px; font-weight: 500; "
            f"background: transparent; padding: 0; letter-spacing: 0.2px;"
        )
        layout.addWidget(header)

        body = QLabel(content)
        body.setWordWrap(True)
        body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        body.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        body.setMaximumWidth(580)
        body.setStyleSheet(
            f"color: #ebebf5; font-size: 13px; line-height: 1.6; "
            f"background: {style['bg']}; border-radius: 12px; padding: 12px 16px;"
        )
        layout.addWidget(body)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.setStyleSheet("background: transparent;")


class ChatWidget(QWidget):
    message_sent = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setStyleSheet(
            "QScrollArea { background: transparent; } "
            "QWidget#chat_messages { background: transparent; }"
        )

        self._messages_widget = QWidget()
        self._messages_widget.setObjectName("chat_messages")
        self._messages_layout = QVBoxLayout(self._messages_widget)
        self._messages_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self._messages_layout.setContentsMargins(20, 20, 20, 12)
        self._messages_layout.setSpacing(4)
        self._messages_layout.addStretch()

        self._scroll.setWidget(self._messages_widget)
        layout.addWidget(self._scroll)

        self._build_input_bar(layout)

    def _build_input_bar(self, parent_layout: QVBoxLayout) -> None:
        bar = QWidget()
        bar.setStyleSheet("""
            QWidget#input_bar {
                background: rgba(44, 44, 46, 180);
                border-top: 1px solid rgba(72, 72, 74, 100);
            }
        """)
        bar.setObjectName("input_bar")

        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(16, 10, 16, 14)
        bar_layout.setSpacing(8)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Message D.A.N.")
        self._input.returnPressed.connect(self._send)
        self._input.setMinimumHeight(36)
        self._input.setStyleSheet("""
            QLineEdit {
                background: rgba(28, 28, 30, 200);
                border: 1px solid #48484a;
                border-radius: 18px;
                padding: 8px 18px;
                color: #ebebf5;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #64d2ff;
            }
        """)
        bar_layout.addWidget(self._input)

        self._send_btn = QPushButton("Send")
        self._send_btn.clicked.connect(self._send)
        self._send_btn.setMinimumHeight(36)
        self._send_btn.setMinimumWidth(80)
        self._send_btn.setStyleSheet("""
            QPushButton {
                background: #64d2ff;
                color: #1c1c1e;
                border: none;
                border-radius: 18px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #8ae1ff;
            }
            QPushButton:pressed {
                background: #4aa8d4;
            }
        """)
        bar_layout.addWidget(self._send_btn)

        parent_layout.addWidget(bar)

    def add_message(self, role: str, content: str) -> None:
        bubble = MessageBubble(role, content)
        pos = self._messages_layout.count() - 1
        self._messages_layout.insertWidget(pos, bubble)
        QTimer.singleShot(50, lambda: self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        ))

    def set_input_enabled(self, enabled: bool) -> None:
        self._input.setEnabled(enabled)
        self._send_btn.setEnabled(enabled)

    def _send(self) -> None:
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self.message_sent.emit(text)
