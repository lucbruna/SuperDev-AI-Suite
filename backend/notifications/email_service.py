"""Email notification service with SMTP support."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)

_EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


def _validate_recipients(recipients: list[str]) -> list[str]:
    """Validate and sanitize email recipients. Returns only valid emails."""
    validated = []
    for r in recipients:
        r = r.strip().lower()
        if _EMAIL_REGEX.match(r):
            validated.append(r)
    if not validated:
        raise ValueError("No valid email recipients provided")
    return validated


class EmailPriority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class EmailMessage:
    to: str | list[str]
    subject: str
    body: str
    html_body: str | None = None
    from_email: str = "noreply@superdev.ai"
    cc: str | list[str] | None = None
    bcc: str | list[str] | None = None
    priority: EmailPriority = EmailPriority.NORMAL
    attachments: list[dict[str, Any]] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EmailResult:
    success: bool
    message_id: str | None = None
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


class EmailService:
    """Email service with SMTP backend and template support."""

    def __init__(
        self,
        smtp_host: str = "localhost",
        smtp_port: int = 587,
        smtp_user: str = "",
        smtp_password: str = "",
        use_tls: bool = True,
        from_email: str = "noreply@superdev.ai",
        dry_run: bool = False,
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.use_tls = use_tls
        self.from_email = from_email
        self.dry_run = dry_run
        self._templates: dict[str, str] = {}
        self._sent_log: list[dict[str, Any]] = []

    def register_template(self, name: str, template: str) -> None:
        self._templates[name] = template

    def render_template(self, name: str, context: dict[str, Any]) -> str:
        template = self._templates.get(name, "")
        for key, value in context.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))
        return template

    async def send(self, message: EmailMessage) -> EmailResult:
        # Validate recipients before sending
        try:
            to_list = message.to if isinstance(message.to, list) else [message.to]
            validated_to = _validate_recipients(to_list)
        except ValueError as e:
            return EmailResult(success=False, error=str(e))

        if self.dry_run:
            result = EmailResult(
                success=True,
                message_id=f"dry-run-{len(self._sent_log)}",
                details={"dry_run": True, "to": validated_to, "subject": message.subject},
            )
            self._sent_log.append({"message": message, "result": result})
            logger.info("Email (dry run): to=%s subject=%s", validated_to, message.subject)
            return result

        try:
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            import aiosmtplib

            msg = MIMEMultipart("alternative")
            msg["From"] = message.from_email or self.from_email
            msg["To"] = ", ".join(validated_to)
            msg["Subject"] = message.subject
            msg["X-Priority"] = str(
                {"low": "5", "normal": "3", "high": "2", "urgent": "1"}.get(message.priority.value, "3")
            )

            if message.cc:
                cc_list = message.cc if isinstance(message.cc, list) else [message.cc]
                msg["Cc"] = ", ".join(cc_list)

            msg.attach(MIMEText(message.body, "plain"))
            if message.html_body:
                msg.attach(MIMEText(message.html_body, "html"))

            recipients = list(validated_to)
            if message.cc:
                cc_list = message.cc if isinstance(message.cc, list) else [message.cc]
                validated_cc = _validate_recipients(cc_list)
                recipients.extend(validated_cc)

            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user or None,
                password=self.smtp_password or None,
                use_tls=self.use_tls,
                recipients=recipients,
            )

            result = EmailResult(success=True, message_id=msg.get("Message-ID", ""))
            self._sent_log.append({"message": message, "result": result})
            logger.info("Email sent: to=%s subject=%s", message.to, message.subject)
            return result

        except Exception as e:
            result = EmailResult(success=False, error=str(e))
            logger.error("Email failed: to=%s error=%s", message.to, e)
            return result

    async def send_template(
        self,
        to: str | list[str],
        template_name: str,
        context: dict[str, Any],
        subject: str | None = None,
        priority: EmailPriority = EmailPriority.NORMAL,
    ) -> EmailResult:
        body = self.render_template(template_name, context)
        msg_subject = subject or f"SuperDev: {template_name}"
        return await self.send(
            EmailMessage(
                to=to,
                subject=msg_subject,
                body=body,
                priority=priority,
            )
        )

    def get_sent_log(self) -> list[dict[str, Any]]:
        return self._sent_log

    def get_stats(self) -> dict[str, Any]:
        return {
            "total_sent": len(self._sent_log),
            "successful": sum(1 for r in self._sent_log if r["result"].success),
            "failed": sum(1 for r in self._sent_log if not r["result"].success),
            "templates": list(self._templates.keys()),
            "dry_run": self.dry_run,
        }


email_service = EmailService()
