from __future__ import annotations

import asyncio
import json
import socket
import time
from typing import Any

from ..database_models import ConnectionConfig, QueryResult
from .base_driver import BaseDriver


class RedisDriver(BaseDriver):
    """Redis driver using stdlib socket for RESP protocol.

    Implements basic Redis commands through the REdis Serialization Protocol.
    Supports string operations, key management, and pub/sub.
    """

    CRLF = b"\r\n"

    def __init__(self, logger: Any = None) -> None:
        super().__init__(logger)
        self._socket: socket.socket | None = None
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

    async def connect(self, config: ConnectionConfig) -> None:
        self._config = config
        try:
            self._reader, self._writer = await asyncio.open_connection(
                config.host, config.port or 6379,
            )
            self._connected = True
            if config.password:
                await self._send_command("AUTH", config.password)
            self._logger.info(f"Redis connected at {config.host}:{config.port or 6379}")
        except (OSError, asyncio.TimeoutError) as exc:
            self._connected = False
            raise ConnectionError(f"Redis connection failed: {exc}") from exc

    async def disconnect(self) -> None:
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception:
                pass
        self._connected = False
        self._logger.info("Redis disconnected")

    async def execute(self, query: str, params: list[Any] | None = None) -> QueryResult:
        self._require_connection()
        parts = query.split()
        cmd = parts[0]
        args = [str(a) for a in (params or [])]
        start = time.monotonic()
        try:
            response = await self._send_command(cmd, *args)
            elapsed = (time.monotonic() - start) * 1000
            return QueryResult(
                rows=[{"result": response}] if response is not None else [],
                row_count=1 if response is not None else 0,
                duration_ms=round(elapsed, 2),
            )
        except Exception as exc:
            elapsed = (time.monotonic() - start) * 1000
            return QueryResult(error=str(exc), duration_ms=round(elapsed, 2))

    async def _send_command(self, cmd: str, *args: str) -> Any:
        if not self._writer:
            raise ConnectionError("Not connected")
        # RESP protocol: *<argc>\r\n$<len>\r\n<arg>\r\n...
        parts = [cmd] + list(args)
        buf = f"*{len(parts)}\r\n"
        for p in parts:
            encoded = p.encode() if isinstance(p, str) else str(p).encode()
            buf += f"${len(encoded)}\r\n".encode().decode() + encoded.decode(errors="replace") + "\r\n"
        self._writer.write(buf.encode())
        await self._writer.drain()
        return await self._read_response()

    async def _read_response(self) -> Any:
        if not self._reader:
            return None
        prefix = await self._reader.read(1)
        if not prefix:
            return None
        if prefix == b"+":
            return (await self._reader.readline()).decode().strip()
        if prefix == b"-":
            error_msg = (await self._reader.readline()).decode().strip()
            raise RuntimeError(f"Redis error: {error_msg}")
        if prefix == b":":
            return int((await self._reader.readline()).decode().strip())
        if prefix == b"$":
            line = (await self._reader.readline()).decode().strip()
            if line == "-1":
                return None
            length = int(line)
            return (await self._reader.readexactly(length + 2))[:-2].decode()
        if prefix == b"*":
            count = int((await self._reader.readline()).decode().strip())
            if count == -1:
                return None
            items = []
            for _ in range(count):
                items.append(await self._read_response())
            return items
        return None

    @property
    def dialect(self) -> str:
        return "redis"

    async def ping(self) -> bool:
        try:
            await self._send_command("PING")
            return True
        except Exception:
            return False
