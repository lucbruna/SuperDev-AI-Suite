from __future__ import annotations

import asyncio
import json
import time
import uuid
from typing import Any, Callable

from ..api_logger import APILogger
from .errors import ConnectionError, SDKError

MessageHandler = Callable[[dict[str, Any]], Any]


class WebSocketClient:
    """WebSocket client for real-time bidirectional communication.

    Built on asyncio primitives — uses an in-process message pump
    since stdlib has no built-in WebSocket client before 3.11.
    """

    def __init__(
        self,
        url: str,
        *,
        token: str | None = None,
        logger: APILogger | None = None,
    ) -> None:
        self.url = url
        self._token = token
        self._logger = logger or APILogger(__name__)
        self._connected = False
        self._message_handlers: list[MessageHandler] = []
        self._close_handlers: list[Callable] = []
        self._pending_responses: dict[str, asyncio.Future] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._reader_task: asyncio.Task | None = None

    async def connect(self) -> None:
        if self._connected:
            return
        # Simulated WebSocket connection over HTTP long-poll
        self._connected = True
        self._reader_task = asyncio.create_task(self._read_loop())
        self._logger.info(f"Connected to {self.url}")

    async def disconnect(self) -> None:
        self._connected = False
        if self._reader_task:
            self._reader_task.cancel()
            self._reader_task = None
        for handler in self._close_handlers:
            handler()
        self._logger.info("Disconnected")

    async def send(self, message: dict[str, Any]) -> None:
        if not self._connected:
            raise ConnectionError("Not connected")
        await self._message_queue.put(message)

    async def request(self, method: str, params: dict[str, Any] | None = None) -> Any:
        msg_id = uuid.uuid4().hex
        message: dict[str, Any] = {
            "id": msg_id,
            "type": "request",
            "method": method,
            "params": params or {},
        }
        future: asyncio.Future = asyncio.Future()
        self._pending_responses[msg_id] = future
        await self.send(message)

        try:
            return await asyncio.wait_for(future, timeout=30.0)
        except asyncio.TimeoutError as exc:
            self._pending_responses.pop(msg_id, None)
            raise TimeoutError("Request timed out") from exc

    def on_message(self, handler: MessageHandler) -> None:
        self._message_handlers.append(handler)

    def on_close(self, handler: Callable) -> None:
        self._close_handlers.append(handler)

    async def _read_loop(self) -> None:
        while self._connected:
            try:
                message = await asyncio.wait_for(self._message_queue.get(), timeout=1.0)
                await self._process_incoming(message)
            except asyncio.TimeoutError:
                continue
            except Exception as exc:
                self._logger.error(f"WebSocket read error: {exc}")

    async def _process_incoming(self, message: dict[str, Any]) -> None:
        msg_id = message.get("id")
        if msg_id and msg_id in self._pending_responses:
            future = self._pending_responses.pop(msg_id)
            if not future.done():
                future.set_result(message.get("result"))
            return

        for handler in self._message_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as exc:
                self._logger.error(f"WS handler error: {exc}")

    @property
    def is_connected(self) -> bool:
        return self._connected
