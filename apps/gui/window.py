from __future__ import annotations

import asyncio
import json
import logging
import struct
from typing import TYPE_CHECKING, override

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from dan.core.tool_registry import ToolRegistry
from dan.plugins.registry import PluginRegistry
from dan.skills.registry import SkillRegistry

from .chat import ChatWidget
from .panels import PluginPanel, SkillPanel, ToolPanel

if TYPE_CHECKING:
    from asyncio import StreamReader, StreamWriter
    from dan.core.config import DANConfig

logger = logging.getLogger("dan.gui")

SERVE_HOST = "127.0.0.1"
SERVE_PORT = 7979


class LoadingOverlay(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._shown = False
        self._opacity = 0.0

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("Thinking")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = QFont()
        f.setPointSize(16)
        f.setWeight(QFont.Weight.Light)
        label.setFont(f)
        label.setStyleSheet("color: #ebebf5; background: transparent;")
        layout.addWidget(label)

        sub = QLabel("processing your request")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sf = QFont()
        sf.setPointSize(11)
        sub.setFont(sf)
        sub.setStyleSheet("color: #636366; background: transparent;")
        layout.addWidget(sub)

        self._fade_timer = QTimer()
        self._fade_timer.timeout.connect(self._step)
        self._fade_timer.start(16)

    def _step(self) -> None:
        if self._shown and self._opacity < 1.0:
            self._opacity = min(self._opacity + 0.06, 1.0)
            self.update()
        elif not self._shown and self._opacity > 0.0:
            self._opacity = max(self._opacity - 0.06, 0.0)
            self.update()
            if self._opacity <= 0.0:
                self.hide()

    @override
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        alpha = min(int(self._opacity * 200), 200)
        painter.fillRect(self.rect(), QColor(28, 28, 30, alpha))
        painter.end()
        super().paintEvent(event)

    def show_thinking(self) -> None:
        self._shown = True
        self.raise_()
        self.show()

    def hide(self) -> None:
        self._shown = False
        super().hide()


class MainWindow(QMainWindow):
    def __init__(self, config: DANConfig) -> None:
        super().__init__()
        self._config = config
        self._loop: asyncio.AbstractEventLoop | None = None
        self._reader: StreamReader | None = None
        self._writer: StreamWriter | None = None
        self._busy = False

        self._registry = ToolRegistry()
        self._registry.discover()
        self._skill_registry = SkillRegistry()
        self._plugin_registry = PluginRegistry()

        self.setWindowTitle("D.A.N.")
        self.setMinimumSize(900, 600)
        self.resize(1100, 720)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._setup_ui()

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._chat = ChatWidget()
        self._chat.message_sent.connect(self._on_message)

        self._side_stack = QStackedWidget()
        self._side_stack.setMinimumWidth(260)
        self._side_stack.setMaximumWidth(320)
        self._side_stack.setStyleSheet("""
            QStackedWidget {
                background: rgba(35, 35, 37, 180);
                border-left: 1px solid #48484a;
            }
        """)
        self._side_stack.addWidget(ToolPanel(self._registry))
        self._side_stack.addWidget(SkillPanel(self._skill_registry))
        self._side_stack.addWidget(PluginPanel(self._plugin_registry))

        main_layout.addWidget(self._chat, stretch=1)
        main_layout.addWidget(self._side_stack)

        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status_label = QLabel("")
        self._status.addPermanentWidget(self._status_label)

        self._overlay = LoadingOverlay(self)
        self._overlay.setGeometry(self.rect())

    @override
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._overlay.setGeometry(self.rect())

    def _setup_menu(self) -> None:
        menubar = self.menuBar()
        fm = menubar.addMenu("File")
        qa = fm.addAction("Quit")
        qa.triggered.connect(self.close)
        hm = menubar.addMenu("Help")
        aa = hm.addAction("About D.A.N.")
        aa.triggered.connect(
            lambda: QMessageBox.about(
                self, "About D.A.N.",
                "D.A.N. - Distributed Assistant Neural-network\n"
                "Connects to the API server (dan serve).",
            )
        )

    def connect_to_server(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        self._status_label.setText("Connecting...")
        loop.create_task(self._do_connect())

    async def _do_connect(self) -> None:
        try:
            r, w = await asyncio.wait_for(
                asyncio.open_connection(SERVE_HOST, SERVE_PORT),
                timeout=5,
            )
            self._reader = r
            self._writer = w
            self._status_label.setText("Ready")
            self._loop.create_task(self._read_loop())
        except TimeoutError:
            self._chat.add_message(
                "error",
                "Could not reach D.A.N. API. Run:\n  dan serve",
            )
            self._status_label.setText("Disconnected")
        except Exception as e:
            self._chat.add_message("error", f"Connection error: {e}")
            self._status_label.setText("Disconnected")

    async def _read_loop(self) -> None:
        assert self._reader is not None
        try:
            while True:
                header = await self._reader.readexactly(4)
                payload_len = struct.unpack("!I", header)[0]
                raw = await self._reader.readexactly(payload_len)
                data = json.loads(raw)
                self._handle_response(data)
        except (asyncio.IncompleteReadError, ConnectionResetError, BrokenPipeError):
            if self._busy:
                self._busy = False
                self._overlay.hide()
                self._chat.set_input_enabled(True)
            self._chat.add_message("error", "API connection lost.")
            self._status_label.setText("Disconnected")

    def _handle_response(self, data: dict) -> None:
        if self._busy:
            self._busy = False
            self._overlay.hide()
            self._chat.set_input_enabled(True)
            self._status_label.setText("Ready")

        text = data.get("text")
        error = data.get("error")
        results = data.get("results") or data.get("steps")

        if error:
            self._chat.add_message("error", error)
        elif results:
            for r in results:
                t = r.get("type", "")
                name = r.get("name", "")
                result_str = r.get("result", "")
                msg = r.get("message", "")
                if t == "confirm":
                    self._chat.add_message("tool", f"Confirm: {msg}")
                elif t == "tool":
                    self._chat.add_message("tool", f"{name}: {result_str}")
                elif t == "error":
                    self._chat.add_message("error", msg)
                else:
                    self._chat.add_message("tool", str(r))
        if text:
            self._chat.add_message("assistant", text)

    def _on_message(self, message: str) -> None:
        if self._busy:
            return
        if not self._writer:
            self._chat.add_message("error", "Not connected.")
            return

        self._chat.add_message("user", message)
        self._chat.set_input_enabled(False)
        self._busy = True
        self._status_label.setText("Thinking...")
        self._overlay.show_thinking()

        async def send() -> None:
            try:
                await _write(self._writer, {"message": message})
            except Exception as e:
                self._busy = False
                self._overlay.hide()
                self._chat.set_input_enabled(True)
                self._status_label.setText("Ready")
                self._chat.add_message("error", f"Send failed: {e}")

        self._loop.create_task(send())

    @override
    def closeEvent(self, event) -> None:
        if self._writer:
            self._writer.close()
        super().closeEvent(event)


async def _write(writer: asyncio.StreamWriter, data: dict) -> None:
    raw = json.dumps(data).encode("utf-8")
    writer.write(struct.pack("!I", len(raw)))
    writer.write(raw)
    await writer.drain()
