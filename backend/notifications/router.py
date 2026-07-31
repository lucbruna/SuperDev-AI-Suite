"""Notification API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import get_current_active_user
from backend.notifications.notification_manager import notification_manager

router = APIRouter(dependencies=[Depends(get_current_active_user)])


class NotificationCreate(BaseModel):
    title: str
    message: str
    notification_type: str = "info"
    data: dict[str, Any] = {}


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    notification_type: str
    is_read: bool
    data: dict[str, Any]
    created_at: str


@router.get("/", response_model=list[NotificationResponse])
async def list_notifications(
    current_user: dict[str, Any] = Depends(get_current_active_user),
    unread_only: bool = False,
) -> list[NotificationResponse]:
    notifs = notification_manager.list_for_user(current_user["id"], unread_only=unread_only)
    return [
        NotificationResponse(
            id=n.id,
            user_id=n.user_id,
            title=n.title,
            message=n.message,
            notification_type=n.notification_type.value,
            is_read=n.is_read,
            data=n.data,
            created_at=n.created_at.isoformat(),
        )
        for n in notifs
    ]


@router.get("/unread-count")
async def unread_count(
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, int]:
    return {"count": notification_manager.unread_count(current_user["id"])}


@router.post("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, str]:
    notif = notification_manager.get(notification_id)
    if not notif or notif.user_id != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    notification_manager.mark_read(notification_id)
    return {"status": "ok"}


@router.post("/read-all")
async def mark_all_read(
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, int]:
    count = notification_manager.mark_all_read(current_user["id"])
    return {"marked": count}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: str,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> None:
    notif = notification_manager.get(notification_id)
    if not notif or notif.user_id != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    notification_manager.delete(notification_id)
