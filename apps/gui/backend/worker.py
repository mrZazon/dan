from __future__ import annotations

import time
from typing import Any

from PyQt6.QtCore import QObject, QThread, pyqtSignal


class SendWorker(QObject):
    """Worker that sends messages to the backend in a background thread."""

    started = pyqtSignal()
    thinking_changed = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, client: Any, message: str,
                 conversation_id: str | None = None,
                 parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._client = client
        self._message = message
        self._conversation_id = conversation_id

    def run(self) -> None:
        """Execute the backend call."""
        self.started.emit()
        self.thinking_changed.emit("Calling model")

        start_time = time.monotonic()

        try:
            resp = self._client.send(self._message, self._conversation_id)
            elapsed = time.monotonic() - start_time

            if resp.error:
                self.error.emit(resp.error)
                return

            self.finished.emit({
                "text": resp.text,
                "results": resp.results,
                "steps": resp.steps,
                "elapsed": elapsed,
            })
        except Exception as e:
            self.error.emit(str(e))


class BackendWorker(QObject):
    """Manages worker threads for backend communication."""

    response_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    thinking_updated = pyqtSignal(str)
    connection_changed = pyqtSignal(bool)

    def __init__(self, client: Any, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._client = client
        self._thread: QThread | None = None
        self._worker: SendWorker | None = None
        self._busy = False
        self._thread_count = 4
        self._timeout = 300

    @property
    def busy(self) -> bool:
        return self._busy

    def send_message(self, message: str, conversation_id: str | None = None) -> None:
        """Send a message to the backend asynchronously."""
        if self._busy:
            return

        self._busy = True

        self._thread = QThread(self)
        self._worker = SendWorker(self._client, message, conversation_id)
        self._worker.moveToThread(self._thread)

        self._worker.started.connect(lambda: self.thinking_updated.emit("Connecting"))
        self._worker.thinking_changed.connect(self.thinking_updated.emit)
        self._worker.finished.connect(self._on_response)
        self._worker.error.connect(self._on_error)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.finished.connect(self._cleanup_thread)

        self._thread.start()

    def check_connection(self) -> bool:
        """Check if backend is reachable."""
        ok = self._client.health_check()
        self.connection_changed.emit(ok)
        return ok

    def _on_response(self, data: dict) -> None:
        self._busy = False
        self.response_received.emit(data)

    def _on_error(self, msg: str) -> None:
        self._busy = False
        self.error_occurred.emit(msg)

    def _cleanup_thread(self) -> None:
        if self._thread:
            self._thread.deleteLater()
            self._thread = None
        if self._worker:
            self._worker.deleteLater()
            self._worker = None

    def set_thread_count(self, n: int) -> None:
        self._thread_count = max(1, n)

    def set_timeout(self, t: int) -> None:
        self._timeout = max(10, t)
