from __future__ import annotations

import json
import logging
import struct
import socket
import uuid
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 7979


@dataclass
class BackendResponse:
    """Parsed response from the DAN backend server."""

    text: str = ""
    results: list[dict[str, Any]] = field(default_factory=list)
    steps: list[dict[str, Any]] = field(default_factory=list)
    error: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.error


class DANClient:
    """Synchronous TCP client for the DAN backend server.

    Protocol: 4-byte big-endian length header + JSON payload.
    Request:  {"message": "...", "conversation_id": "..."}
    Response: {"text": "...", "results": [...], "steps": [...], "error": "..."}
    """

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
        self._host = host
        self._port = port
        self._sock: socket.socket | None = None
        self._conversation_id: str | None = None

    def new_conversation(self) -> str:
        """Generate a new conversation ID."""
        self._conversation_id = str(uuid.uuid4())[:8]
        return self._conversation_id

    @property
    def connected(self) -> bool:
        return self._sock is not None

    def connect(self) -> bool:
        """Establish TCP connection to the backend server."""
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(10.0)
            self._sock.connect((self._host, self._port))
            self._sock.settimeout(300.0)
            logger.info("Connected to backend at %s:%d", self._host, self._port)
            return True
        except (socket.error, OSError) as e:
            logger.warning("Connection failed: %s", e)
            self._sock = None
            return False

    def disconnect(self) -> None:
        """Close the TCP connection."""
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
            logger.info("Disconnected from backend")

    def send(self, message: str, conversation_id: str | None = None) -> BackendResponse:
        """Send a message and return the response."""
        if not self._sock:
            return BackendResponse(error="Not connected to backend")

        payload: dict[str, Any] = {"message": message}
        cid = conversation_id or self._conversation_id
        if cid:
            payload["conversation_id"] = cid
        req = json.dumps(payload).encode("utf-8")
        try:
            self._sock.sendall(struct.pack("!I", len(req)) + req)
        except (socket.error, OSError) as e:
            self._sock = None
            return BackendResponse(error=f"Send failed: {e}")

        return self._recv()

    def health_check(self) -> bool:
        """Check if the backend server is reachable."""
        if not self._sock:
            return self.connect()
        try:
            self._sock.sendall(struct.pack("!I", 0))
            return True
        except (socket.error, OSError):
            self._sock = None
            return False

    def _recv(self) -> BackendResponse:
        """Read a response from the backend."""
        if not self._sock:
            return BackendResponse(error="Not connected")

        try:
            header = self._recv_exact(4)
            if header is None:
                return BackendResponse(error="Connection closed by server")
            payload_len = struct.unpack("!I", header)[0]
            if payload_len == 0:
                return BackendResponse(error="Empty response from server")
            raw = self._recv_exact(payload_len)
            if raw is None:
                return BackendResponse(error="Connection closed during response")
            data = json.loads(raw)
            return BackendResponse(
                text=data.get("text", ""),
                results=data.get("results", []),
                steps=data.get("steps", []),
                error=data.get("error", ""),
                raw=data,
            )
        except (json.JSONDecodeError, struct.error) as e:
            return BackendResponse(error=f"Invalid response: {e}")
        except (socket.error, OSError) as e:
            self._sock = None
            return BackendResponse(error=f"Receive failed: {e}")

    def _recv_exact(self, n: int) -> bytes | None:
        """Read exactly n bytes from the socket."""
        if not self._sock:
            return None
        data = b""
        while len(data) < n:
            try:
                chunk = self._sock.recv(n - len(data))
                if not chunk:
                    return None
                data += chunk
            except (socket.error, OSError):
                return None
        return data
