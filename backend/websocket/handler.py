"""WebSocket handler with token authentication."""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from backend.websocket.events import EventType, WSEvent
from backend.websocket.manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    channel: str = Query(default="default"),
    token: str | None = Query(default=None),
):
    # Verify token before accepting connection
    if not token:
        await websocket.close(code=4001, reason="Authentication token required")
        return

    try:
        from backend.auth.jwt import get_jwt_manager

        mgr = get_jwt_manager()
        payload = await mgr.verify_token(token)
        if payload is None:
            await websocket.close(code=4003, reason="Invalid or expired token")
            return
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=4003, reason="Invalid token payload")
            return
    except Exception:
        logger.exception("WebSocket authentication failed")
        await websocket.close(code=4003, reason="Authentication failed")
        return

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
                    raw_type = message.get("event_type", "notification")
                    event_type = (
                        EventType[raw_type]
                        if isinstance(raw_type, str) and raw_type in EventType.__members__
                        else EventType.LOG_MESSAGE
                    )
                    event = WSEvent(
                        type=event_type,
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
            except Exception:
                # Malformed/unexpected message — notify the client and keep the
                # connection alive instead of tearing down the whole session.
                logger.warning("Unexpected message error on channel %s", channel, exc_info=True)
                await manager.send_personal(
                    {"type": "error", "message": "Invalid message"},
                    websocket,
                )
    except WebSocketDisconnect:
        # Normal client disconnect — nothing else to log.
        pass
    except Exception:
        logger.exception("Unexpected WebSocket error on channel %s", channel)
    finally:
        # Always remove the socket from the manager, even on unexpected
        # errors, so no dead connections leak into broadcasts.
        await manager.disconnect(websocket, channel)
