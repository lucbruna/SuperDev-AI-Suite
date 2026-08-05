"""Graph WebSocket: real-time events for connected dashboard clients.

Clients connect to ``/ws`` and receive graph lifecycle events published on
the module's event bus (builds, refreshes, errors, scheduled scans).
"""
from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from modules.architecture_graph.websocket.events import get_bus
from modules.architecture_graph.websocket.manager import manager

router = APIRouter(tags=["Architecture Graph — Realtime"])


@router.websocket("/ws")
async def graph_ws(websocket: WebSocket) -> None:
    """Live event stream. Client may send a ping; server pushes events."""
    await manager.connect(websocket)

    bus = get_bus()
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    def forward(event: dict[str, Any]) -> None:
        try:
            loop.call_soon_threadsafe(queue.put_nowait, event)
        except Exception:
            pass

    unsubscribe = bus.subscribe(forward)
    try:
        # Acknowledge connection immediately.
        await websocket.send_json({"type": "connected", "data": {"service": "architecture-graph"}})
        while True:
            # Wait for inbound message OR bus event.
            inbound = asyncio.create_task(websocket.receive_text())
            event_task = asyncio.create_task(queue.get())
            done, _ = await asyncio.wait(
                {inbound, event_task}, return_when=asyncio.FIRST_COMPLETED
            )
            if inbound in done:
                try:
                    message = inbound.result()
                except Exception:
                    break
                if message.strip() == "ping":
                    await websocket.send_json({"type": "pong"})
                inbound.cancel()
            else:
                inbound.cancel()
            if event_task in done:
                event = event_task.result()
                await websocket.send_json(event)
            event_task.cancel()
    except WebSocketDisconnect:
        pass
    finally:
        unsubscribe()
        manager.disconnect(websocket)
