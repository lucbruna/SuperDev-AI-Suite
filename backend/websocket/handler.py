from __future__ import annotations

import json

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from backend.websocket.events import EventType, WSEvent
from backend.websocket.manager import manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    channel: str = Query(default="default"),
    token: str | None = Query(default=None),
):
    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                msg_type = message.get("type", "")

                if msg_type == EventType.PING.value:
                    await manager.send_personal(
                        {"type": EventType.PONG.value, "channel": channel},
                        websocket,
                    )
                elif msg_type == "subscribe":
                    new_channel = message.get("channel", channel)
                    await manager.disconnect(websocket, channel)
                    channel = new_channel
                    await manager.connect(websocket, channel)
                    await manager.send_personal(
                        {"type": "subscribed", "channel": channel},
                        websocket,
                    )
                elif msg_type == "broadcast":
                    event = WSEvent(
                        type=EventType(message.get("event_type", "notification")),
                        channel=channel,
                        data=message.get("data", {}),
                    )
                    await manager.broadcast(channel, event.to_dict())
                else:
                    await manager.send_personal(
                        {"type": "echo", "data": message},
                        websocket,
                    )
            except json.JSONDecodeError:
                await manager.send_personal(
                    {"type": "error", "message": "Invalid JSON"},
                    websocket,
                )
    except WebSocketDisconnect:
        await manager.disconnect(websocket, channel)
