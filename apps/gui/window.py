from __future__ import annotations

import time
import uuid

from pathlib import Path

from PyQt6.QtCore import QProcess, QSettings, QTimer
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtWidgets import QHBoxLayout, QMainWindow, QVBoxLayout, QWidget

from dan.memory.chats import ChatStore

from .backend.client import DANClient
from .backend.worker import BackendWorker
from .chat.area import ChatArea
from .chat.input import InputArea
from .dialogs.settings import SettingsDialog
from .panels.inspector import Inspector
from .panels.status import StatusBar
from .sidebar.panel import Sidebar
from .theme.palette import ThemeManager


class MainWindow(QMainWindow):
    """TUI-style desktop application.

    The conversation IS the interface.
    Sidebar toggles. Inspector toggles. Everything else stays out of the way.
    """

    def __init__(self) -> None:
        super().__init__()
        self._settings = QSettings("DAN", "DAN")
        self._theme_manager = ThemeManager(self)
        self._client = DANClient()
        self._worker = BackendWorker(self._client, self)
        self._server_process: QProcess | None = None
        self._send_time = 0.0

        self._conversations: list[dict] = []
        self._current_conv: dict | None = None
        self._chat_counter = 0
        self._chat_store = ChatStore()

        self.setWindowTitle("D.A.N.")
        self.setMinimumSize(800, 500)
        self.resize(1200, 750)
        icon_path = str(Path(__file__).resolve().parents[2] / "icon" / "icon-dark.png")
        self.setWindowIcon(QIcon(icon_path))

        self._setup_ui()
        self._setup_shortcuts()
        self._connect_signals()

        self._apply_settings()
        self._load_conversations()

        QTimer.singleShot(500, self._initial_connect)

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        self.statusBar().setVisible(False)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        top = QWidget()
        self._top_layout = QHBoxLayout(top)
        self._top_layout.setContentsMargins(0, 0, 0, 0)
        self._top_layout.setSpacing(0)

        self._sidebar = Sidebar(top)
        self._top_layout.addWidget(self._sidebar)

        self._workspace = QWidget()
        ws = QVBoxLayout(self._workspace)
        ws.setContentsMargins(0, 0, 0, 0)
        ws.setSpacing(0)

        self._chat_area = ChatArea(self._workspace)
        ws.addWidget(self._chat_area, 1)

        self._input_area = InputArea(self._workspace)
        ws.addWidget(self._input_area)

        self._top_layout.addWidget(self._workspace, 1)

        self._inspector = Inspector(top)
        self._top_layout.addWidget(self._inspector)

        root.addWidget(top, 1)

        self._status_bar = StatusBar(central)
        root.addWidget(self._status_bar)

    def _setup_shortcuts(self) -> None:
        def add_shortcut(key: str, slot) -> None:  # noqa: A001
            action = QAction(self)
            action.setShortcut(QKeySequence(key))
            action.triggered.connect(slot)
            self.addAction(action)

        add_shortcut("Ctrl+B", self._toggle_sidebar)
        add_shortcut("Ctrl+N", self._on_new_chat)
        add_shortcut("Ctrl+H", lambda: None)
        add_shortcut("Ctrl+M", lambda: None)
        add_shortcut("Ctrl+I", self._toggle_inspector)
        add_shortcut("Ctrl+L", self._on_clear)
        add_shortcut("Ctrl+,", self._on_settings)
        add_shortcut("Escape", self._on_escape)

    def _connect_signals(self) -> None:
        self._input_area.message_submitted.connect(self._on_send)
        self._worker.response_received.connect(self._on_response)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.thinking_updated.connect(self._on_thinking_update)
        self._worker.connection_changed.connect(self._on_connection_changed)

        self._sidebar.new_chat_clicked.connect(self._on_new_chat)
        self._sidebar.settings_clicked.connect(self._on_settings)
        self._sidebar.chat_selected.connect(self._on_chat_selected)

        self._theme_manager.theme_changed.connect(self._reapply_theme)

    def _load_conversations(self) -> None:
        saved = self._chat_store.conversations
        self._conversations.clear()
        self._sidebar.clear_recent_chats()
        max_num = 0
        for conv in saved:
            self._conversations.append(conv)
            self._sidebar.add_recent_chat(conv.get("title", "Chat"))
            title = conv.get("title", "")
            if title.startswith("Chat ") and title[5:].isdigit():
                max_num = max(max_num, int(title[5:]))
        self._chat_counter = max_num
        if self._conversations:
            self._on_chat_selected(0)
            self._sidebar.collapse()

    def _create_conversation(self) -> dict:
        self._chat_counter += 1
        conv_id = str(uuid.uuid4())[:8]
        title = f"Chat {self._chat_counter}"
        conv = {"id": conv_id, "title": title, "messages": []}
        self._conversations.append(conv)
        self._sidebar.add_recent_chat(title)
        self._chat_store.add(conv)
        self._current_conv = conv
        self._client.new_conversation()
        return conv

    def _apply_settings(self) -> None:
        s = self._settings

        model = str(s.value("default_model", "dan-persona"))
        self._saved_model = model
        self._input_area.set_model(model)

        auto = s.value("auto_connect", "Yes")
        self._auto_connect = auto == "Yes"

        self._theme_manager.set_mode_from_string(str(s.value("theme_mode", "Dark")))
        self._theme_manager.set_accent(str(s.value("accent_color", "#7289c8")))

        compact = str(s.value("compact_mode", "Off"))
        self._compact_mode = compact == "On"

        anim = str(s.value("animations", "On"))
        self._animations_enabled = anim == "On"

        threads = int(s.value("worker_threads", "4"))
        self._worker.set_thread_count(threads)

        timeout = int(s.value("request_timeout", "300"))
        self._worker.set_timeout(timeout)

    def _reapply_theme(self, mode: str) -> None:
        from PyQt6.QtWidgets import QApplication
        qapp = QApplication.instance()
        if qapp:
            qapp.setStyleSheet(self._theme_manager.stylesheet())
        self._sidebar.reload_theme(mode)
        self._input_area.reload_theme(mode)
        self._chat_area.reload_theme(mode)
        self._status_bar.reload_theme(mode)
        self._inspector.reload_theme(mode)

    def _kill_existing_server(self) -> None:
        import subprocess
        try:
            result = subprocess.run(
                ["pgrep", "-f", "apps.cli.main serve"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                pids = result.stdout.strip().splitlines()
                for pid in pids:
                    subprocess.run(["kill", pid], capture_output=True, timeout=3)
                import time
                time.sleep(1)
        except Exception:
            pass

    def _start_server(self) -> None:
        import sys
        proc = QProcess(self)
        proc.setProgram(sys.executable)
        proc.setArguments(["-m", "apps.cli.main", "serve"])
        proc.setProcessChannelMode(QProcess.ProcessChannelMode.ForwardedChannels)
        proc.start()
        self._server_process = proc

    def _initial_connect(self) -> None:
        self._status_bar.set_value("state", "Connecting")
        self._kill_existing_server()
        self._inspector.set_value("backend", "Connection", "Starting server...")
        self._start_server()
        QTimer.singleShot(3000, self._retry_connect)

    def _retry_connect(self) -> None:
        ok = self._worker.check_connection()
        if ok:
            self._inspector.set_value("backend", "Connection", "Online")
            self._input_area.set_model(self._saved_model)
        else:
            self._inspector.set_value("backend", "Connection", "Offline")

    def _on_send(self, message: str) -> None:
        if self._worker.busy:
            return

        if self._current_conv is None:
            self._create_conversation()

        msg = {"type": "user", "text": message}
        self._chat_store.add_message(self._current_conv["id"], msg)
        self._chat_area.add_user_message(message)

        turns = self._count_turns()
        self._sidebar.set_memory(f"{turns} turns")
        self._inspector.set_value("session", "Messages", str(turns + 1))
        self._inspector.set_value("session", "Turns", str(turns))

        self._send_time = time.monotonic()
        self._chat_area.show_thinking("Calling model")
        self._status_bar.set_value("state", "Processing")
        self._status_bar.start_pulse()
        self._input_area.set_enabled(False)

        conv_id = self._current_conv["id"]
        self._worker.send_message(message, conv_id)

    def _on_response(self, data: dict) -> None:
        elapsed = data.get("elapsed", 0)
        text = data.get("text", "")
        results = data.get("results", [])
        steps = data.get("steps", [])

        self._chat_area.hide_thinking()

        for step in steps:
            if step.get("type") == "tool":
                name = step.get("name", "")
                result = step.get("result", "")
                msg = {"type": "tool", "name": name, "result": result}
                self._chat_store.add_message(self._current_conv["id"], msg)
                self._chat_area.add_tool_result(name, result)

        for r in results:
            if r.get("type") == "tool":
                msg = {"type": "tool", "name": r.get("name", ""), "result": r.get("result", "")}
                self._chat_store.add_message(self._current_conv["id"], msg)
                self._chat_area.add_tool_result(
                    r.get("name", ""), r.get("result", "")
                )

        if text:
            msg = {"type": "assistant", "text": text}
            self._chat_store.add_message(self._current_conv["id"], msg)
            self._chat_area.add_assistant_message(text)
        elif not results and not steps:
            fallback = "No response from backend."
            msg = {"type": "assistant", "text": fallback}
            self._chat_store.add_message(self._current_conv["id"], msg)
            self._chat_area.add_assistant_message(fallback)

        self._update_stats(elapsed)
        self._status_bar.set_value("state", "Idle")
        self._status_bar.stop_pulse()
        self._input_area.set_enabled(True)
        self._input_area.focus_input()
        turns = self._count_turns()
        self._inspector.set_value("context", "Tokens", f"~{turns * 128}")
        self._inspector.set_value("context", "Usage", f"{turns} messages")

    def _on_error(self, error_msg: str) -> None:
        self._chat_area.hide_thinking()
        self._chat_area.add_assistant_message(f"Error: {error_msg}")
        if self._current_conv:
            msg = {"type": "assistant", "text": f"Error: {error_msg}"}
            self._chat_store.add_message(self._current_conv["id"], msg)
        self._status_bar.set_value("state", "Error")
        self._status_bar.stop_pulse()
        self._input_area.set_enabled(True)

    def _on_thinking_update(self, status: str) -> None:
        self._chat_area.update_thinking(status)
        self._status_bar.set_value("state", status)

    def _on_connection_changed(self, connected: bool) -> None:
        self._status_bar.set_connected(connected)
        self._sidebar.set_connection("Connected" if connected else "Disconnected")
        self._inspector.set_value(
            "backend", "Connection", "Online" if connected else "Offline"
        )
        if connected:
            self._inspector.set_value("backend", "Provider", "ollama")
            self._input_area.set_model(self._saved_model)

    def _on_new_chat(self) -> None:
        self._chat_area.clear()
        self._create_conversation()
        self._sidebar.set_memory("0 turns")
        self._inspector.set_value("session", "Messages", "0")
        self._inspector.set_value("session", "Turns", "0")
        self._status_bar.set_value("state", "Idle")
        self._sidebar.collapse()
        self._input_area.focus_input()
        self._apply_settings()

    def _on_chat_selected(self, row: int) -> None:
        if 0 <= row < len(self._conversations):
            conv = self._conversations[row]
            self._current_conv = conv
            self._chat_area.clear()
            for msg in conv["messages"]:
                if msg["type"] == "user":
                    self._chat_area.add_user_message(msg["text"])
                elif msg["type"] == "assistant":
                    self._chat_area.add_assistant_message(msg["text"])
                elif msg["type"] == "tool":
                    self._chat_area.add_tool_result(msg["name"], msg["result"])
            self._inspector.set_value("session", "Messages", str(len(conv["messages"])))
            self._inspector.set_value("session", "Turns", "0")
            self._status_bar.set_value("state", "Idle")
            self._input_area.focus_input()

    def _on_clear(self) -> None:
        self._chat_area.clear()
        if self._current_conv:
            self._current_conv["messages"] = []
            self._chat_store.update(self._current_conv["id"], messages=[])
        self._status_bar.set_value("state", "Idle")
        self._input_area.focus_input()

    def _on_settings(self) -> None:
        dialog = SettingsDialog(self)
        dialog.settings_changed.connect(self._apply_settings)
        dialog.exec()

    def _toggle_sidebar(self) -> None:
        self._sidebar.toggle()

    def _toggle_inspector(self) -> None:
        self._inspector.toggle()

    def _on_escape(self) -> None:
        if self._sidebar.expanded:
            self._sidebar.collapse()
        elif self._inspector.expanded:
            self._inspector.collapse()
        else:
            self._input_area.focus_input()

    def _update_stats(self, elapsed: float) -> None:
        latency_ms = f"{elapsed * 1000:.0f}ms"
        self._status_bar.set_value("state", f"Idle ({elapsed:.1f}s)")
        turns = self._count_turns()
        self._status_bar.set_value("tokens", f"{turns} turns")
        self._inspector.set_value("performance", "Latency", latency_ms)
        self._inspector.set_value("performance", "Gen time", f"{elapsed:.1f}s")

    def _count_turns(self) -> int:
        from .chat.widgets import AssistantMessage, UserMessage
        return (
            len(self._chat_area.findChildren(UserMessage))
            + len(self._chat_area.findChildren(AssistantMessage))
        )

    def closeEvent(self, event) -> None:  # noqa: N802
        self._client.disconnect()
        self._chat_store.flush()
        if self._server_process:
            state = self._server_process.state()
            if state != QProcess.ProcessState.NotRunning:
                self._server_process.terminate()
            if not self._server_process.waitForFinished(3000):
                self._server_process.kill()
                self._server_process.waitForFinished(2000)
        super().closeEvent(event)
