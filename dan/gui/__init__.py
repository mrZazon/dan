"""D.A.N. GUI — KDE Plasma 6 native interface.

A floating assistant window with system tray integration.
"""
from __future__ import annotations

import asyncio
import sys
import threading
from typing import Any

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QAction
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QSystemTrayIcon,
    QMenu,
    QLabel,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import pyqtSlot


class VoiceWorker(QThread):
    """Background thread for voice recognition + D.A.N. processing."""

    user_said = pyqtSignal(str)
    dan_said = pyqtSignal(str)
    thinking = pyqtSignal(bool)
    listening = pyqtSignal(bool)
    speaking = pyqtSignal(bool)

    def __init__(self, router: Any = None, tts: Any = None, stt: Any = None) -> None:
        super().__init__()
        self._router = router
        self._tts = tts
        self._stt = stt
        self._loop = asyncio.new_event_loop()

    def run(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def submit(self, coro: Any) -> Any:
        return asyncio.run_coroutine_threadsafe(coro, self._loop)


class DanWindow(QMainWindow):
    """Main floating assistant window."""

    def __init__(
        self,
        router: Any = None,
        tts: Any = None,
        stt: Any = None,
    ) -> None:
        super().__init__()
        self._router = router
        self._tts = tts
        self._stt = stt
        self._voice_worker = VoiceWorker(router, tts, stt)
        self._voice_worker.dan_said.connect(self._on_dan_said)
        self._voice_worker.user_said.connect(self._on_user_said)
        self._voice_worker.thinking.connect(self._on_thinking)
        self._voice_worker.listening.connect(self._on_listening)
        self._voice_worker.speaking.connect(self._on_speaking)
        self._voice_worker.start()

        self._setup_ui()
        self._setup_tray()

    def _setup_ui(self) -> None:
        self.setWindowTitle("D.A.N.")
        self.setFixedSize(400, 600)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Main container
        container = QWidget()
        container.setObjectName("container")
        container.setStyleSheet("""
            #container {
                background: rgba(20, 20, 30, 240);
                border-radius: 16px;
                border: 1px solid rgba(100, 255, 100, 80);
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Header
        header = QHBoxLayout()
        title = QLabel("D.A.N.")
        title.setStyleSheet("color: #66ff66; font-size: 18px; font-weight: bold; background: transparent;")
        header.addWidget(title)

        self._status_label = QLabel("●")
        self._status_label.setStyleSheet("color: #66ff66; font-size: 14px; background: transparent;")
        header.addWidget(self._status_label)
        header.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                color: #888; background: transparent; border: none;
                font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { color: #ff4444; }
        """)
        close_btn.clicked.connect(self.hide)
        header.addWidget(close_btn)

        layout.addLayout(header)

        # Chat area
        self._chat = QTextEdit()
        self._chat.setReadOnly(True)
        self._chat.setStyleSheet("""
            QTextEdit {
                color: #e0e0e0;
                background: transparent;
                border: none;
                font-size: 13px;
                font-family: 'Segoe UI', 'Noto Sans', sans-serif;
                padding: 8px;
            }
        """)
        layout.addWidget(self._chat)

        # Input area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Type or press 🎤 to talk...")
        self._input.setStyleSheet("""
            QLineEdit {
                color: #e0e0e0;
                background: rgba(40, 40, 50, 200);
                border: 1px solid rgba(100, 255, 100, 60);
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(100, 255, 100, 120);
            }
        """)
        self._input.returnPressed.connect(self._send_text)
        input_layout.addWidget(self._input)

        self._mic_btn = QPushButton("🎤")
        self._mic_btn.setFixedSize(36, 36)
        self._mic_btn.setStyleSheet("""
            QPushButton {
                background: rgba(100, 255, 100, 40);
                border: 1px solid rgba(100, 255, 100, 80);
                border-radius: 18px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: rgba(100, 255, 100, 80);
            }
            QPushButton:pressed {
                background: rgba(100, 255, 100, 120);
            }
        """)
        self._mic_btn.clicked.connect(self._start_listening)
        input_layout.addWidget(self._mic_btn)

        layout.addLayout(input_layout)

        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(100, 255, 100, 60))
        shadow.setOffset(0, 0)
        container.setGraphicsEffect(shadow)

        self.setCentralWidget(container)

        # Make draggable
        self._drag_pos = None

    def mousePressEvent(self, event: Any) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: Any) -> None:
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: Any) -> None:
        self._drag_pos = None

    def _setup_tray(self) -> None:
        self._tray = QSystemTrayIcon(self)

        # Create green circle icon
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(100, 255, 100))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, 24, 24)
        painter.end()

        self._tray.setIcon(QIcon(pixmap))
        self._tray.setToolTip("D.A.N. — Assistant")

        menu = QMenu()
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        menu.addAction(show_action)

        voice_action = QAction("Voice Chat", self)
        voice_action.triggered.connect(self._start_listening)
        menu.addAction(voice_action)

        menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self._quit)
        menu.addAction(quit_action)

        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._tray_activated)
        self._tray.show()

    def _tray_activated(self, reason: Any) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.raise_()
            self.activateWindow()

    def _quit(self) -> None:
        self._voice_worker.quit()
        QApplication.quit()

    def _send_text(self) -> None:
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self._add_message("you", text)

        # Process in background
        self._voice_worker.thinking.emit(True)
        future = self._voice_worker.submit(self._process_message(text))
        future.add_done_callback(lambda f: self._voice_worker.thinking.emit(False))

    async def _process_message(self, text: str) -> None:
        if not self._router:
            self._voice_worker.dan_said.emit("No router connected.")
            return

        try:
            steps_log = await self._router.route_agentic(text, max_steps=5)
            if steps_log:
                last = steps_log[-1]
                if last.get("type") == "response":
                    response = last["text"]
                elif last.get("type") == "done":
                    response = last.get("summary", "Done.")
                else:
                    response = "Done."
            else:
                response = "I couldn't process that."

            self._voice_worker.dan_said.emit(response)

            # Speak with TTS
            if self._tts:
                self._voice_worker.speaking.emit(True)
                self._tts.speak(response)
                self._voice_worker.speaking.emit(False)

        except Exception as e:
            self._voice_worker.dan_said.emit(f"Error: {e}")

    def _start_listening(self) -> None:
        if not self._stt:
            self._add_message("system", "Voice recognition not available.")
            return
        self._voice_worker.listening.emit(True)
        future = self._voice_worker.submit(self._listen_and_process())
        future.add_done_callback(lambda f: self._voice_worker.listening.emit(False))

    async def _listen_and_process(self) -> None:
        if not self._stt:
            return
        text = await asyncio.get_event_loop().run_in_executor(
            None, self._stt.listen_stream
        )
        if text:
            self._voice_worker.user_said.emit(text)
            await self._process_message(text)

    @pyqtSlot(str)
    def _on_dan_said(self, text: str) -> None:
        self._add_message("dan", text)

    @pyqtSlot(str)
    def _on_user_said(self, text: str) -> None:
        self._add_message("you", text)

    @pyqtSlot(bool)
    def _on_thinking(self, active: bool) -> None:
        self._status_label.setText("⏳" if active else "●")
        self._status_label.setStyleSheet(
            "color: #ffaa00; font-size: 14px; background: transparent;"
            if active else
            "color: #66ff66; font-size: 14px; background: transparent;"
        )

    @pyqtSlot(bool)
    def _on_listening(self, active: bool) -> None:
        self._status_label.setText("🎤" if active else "●")
        self._status_label.setStyleSheet(
            "color: #ff6666; font-size: 14px; background: transparent;"
            if active else
            "color: #66ff66; font-size: 14px; background: transparent;"
        )

    @pyqtSlot(bool)
    def _on_speaking(self, active: bool) -> None:
        self._status_label.setText("🔊" if active else "●")
        self._status_label.setStyleSheet(
            "color: #66aaff; font-size: 14px; background: transparent;"
            if active else
            "color: #66ff66; font-size: 14px; background: transparent;"
        )

    def _add_message(self, sender: str, text: str) -> None:
        if sender == "you":
            color = "#66ccff"
            prefix = "<b>you</b>"
        elif sender == "dan":
            color = "#66ff66"
            prefix = "<b style='color:#66ff66'>D.A.N.</b>"
        else:
            color = "#888888"
            prefix = "<i>system</i>"

        html = f"""
        <div style="margin: 6px 0;">
            <span style="color:{color}; font-size:13px;">{prefix}</span><br>
            <span style="color:#e0e0e0; font-size:13px;">{text}</span>
        </div>
        """
        self._chat.append(html)

        # Auto-scroll
        scrollbar = self._chat.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


def launch_gui(
    router: Any = None,
    tts: Any = None,
    stt: Any = None,
) -> None:
    """Launch the D.A.N. GUI."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = DanWindow(router=router, tts=tts, stt=stt)
    window.show()

    sys.exit(app.exec())
