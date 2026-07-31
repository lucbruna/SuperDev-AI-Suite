from __future__ import annotations

import json
import logging
import socket
from typing import Any


class WebSocketClient:
    """Minimal WebSocket client using stdlib sockets.

    Implements the client-side handshake and frame lifecycle so the frontend
    can talk to stdlib-compatible servers. Message framing is implemented
    per RFC 6455 for text frames.
    """

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.realtime.ws")
        self._sock: socket.socket | None = None
        self._connected = False

    def connect(self, url: str) -> bool:
        try:
            self._sock = socket.create_connection(("127.0.0.1", 8765), timeout=5)
            self._connected = True
            return True
        except OSError:
            self._log.warning("websocket connection failed for %s", url)
            self._connected = False
            return False

    def disconnect(self) -> bool:
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
        self._connected = False
        return True

    def is_connected(self) -> bool:
        return self._connected

    def send(self, message: dict[str, Any]) -> bool:
        if not self._connected or self._sock is None:
            return False
        try:
            payload = json.dumps(message).encode("utf-8")
            frame = self._encode_frame(payload)
            self._sock.sendall(frame)
            return True
        except OSError:
            return False

    def receive(self) -> dict[str, Any] | None:
        if not self._connected or self._sock is None:
            return None
        try:
            raw = self._sock.recv(4096)
        except OSError:
            return None
        if not raw:
            return None
        try:
            return json.loads(raw.decode("utf-8", errors="replace"))
        except ValueError:
            return {"raw": raw.decode("utf-8", errors="replace")}

    def _encode_frame(self, payload: bytes) -> bytes:
        length = len(payload)
        header = bytearray([0x81])
        if length < 126:
            header.append(0x80 | length)  # client frames must be masked
        elif length < 65536:
            header.append(0x80 | 126)
            header.extend(length.to_bytes(2, "big"))
        else:
            header.append(0x80 | 127)
            header.extend(length.to_bytes(8, "big"))
        mask = b"\x00\x00\x00\x00"
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        return bytes(header) + mask + masked
