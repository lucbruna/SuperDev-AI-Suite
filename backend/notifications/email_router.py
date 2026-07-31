"""Email notification API routes."""

from __future__ import annotations

from typing import Any

from backend.dependencies import get_current_active_user
from backend.notifications.email_service import EmailPriority, email_service
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter(dependencies=[Depends(get_current_active_user)])


class SendEmailRequest(BaseModel):
    to: str | list[str]
    subject: str
    body: str
    html_body: str | None = None
    priority: str = "normal"
    tags: list[str] = []


class SendTemplateRequest(BaseModel):
    to: str | list[str]
    template_name: str
    context: dict[str, Any] = {}
    subject: str | None = None
    priority: str = "normal"


class RegisterTemplateRequest(BaseModel):
    name: str
    template: str


@router.post("/send")
async def send_email(
    request: SendEmailRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    from backend.notifications.email_service import EmailMessage

    msg = EmailMessage(
        to=request.to,
        subject=request.subject,
        body=request.body,
        html_body=request.html_body,
        priority=EmailPriority(request.priority),
        tags=request.tags,
    )
    result = await email_service.send(msg)
    return {
        "success": result.success,
        "message_id": result.message_id,
        "error": result.error,
    }


@router.post("/send-template")
async def send_template(
    request: SendTemplateRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    result = await email_service.send_template(
        to=request.to,
        template_name=request.template_name,
        context=request.context,
        subject=request.subject,
        priority=EmailPriority(request.priority),
    )
    return {
        "success": result.success,
        "message_id": result.message_id,
        "error": result.error,
    }


@router.post("/templates")
async def register_template(
    request: RegisterTemplateRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, str]:
    email_service.register_template(request.name, request.template)
    return {"name": request.name, "status": "registered"}


@router.get("/stats")
async def email_stats(
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    return email_service.get_stats()
