from __future__ import annotations

import json
import logging
import smtplib
from dataclasses import dataclass, field
from email.mime.text import MIMEText
from typing import Any, Literal

from ..monitoring_models import Alert

from .alert_notifier import AlertNotifier


ChannelType = Literal["email", "slack", "webhook", "pagerduty", "sms"]


@dataclass
class ChannelConfig:
    type: ChannelType = "webhook"
    name: str = ""
    enabled: bool = True
    config: dict[str, Any] = field(default_factory=dict)


class EmailAlertChannel(AlertNotifier):
    """Sends alert notifications via email."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._smtp_host = config.get("smtp_host", "localhost")
        self._smtp_port = config.get("smtp_port", 25)
        self._username = config.get("username", "")
        self._password = config.get("password", "")
        self._from_addr = config.get("from_addr", "alerts@superdev")
        self._to_addrs = config.get("to_addrs", [])
        self._use_tls = config.get("use_tls", False)

    def notify(self, alert: Alert) -> None:
        subject = f"[{alert.severity.value.upper()}] {alert.name}"
        body = (
            f"Alert: {alert.name}\n"
            f"Severity: {alert.severity.value}\n"
            f"Status: {alert.status.value}\n"
            f"Message: {alert.message}\n"
            f"Value: {alert.value}\n"
            f"Threshold: {alert.threshold}\n"
        )

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self._from_addr
        msg["To"] = ", ".join(self._to_addrs)

        try:
            with smtplib.SMTP(self._smtp_host, self._smtp_port) as server:
                if self._use_tls:
                    server.starttls()
                if self._username:
                    server.login(self._username, self._password)
                server.sendmail(self._from_addr, self._to_addrs, msg.as_string())
        except Exception as e:
            logger = logging.getLogger("superdev.alerts")
            logger.error("Failed to send alert email: %s", e)


class SlackAlertChannel(AlertNotifier):
    """Sends alert notifications via Slack webhook."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._webhook_url = config.get("webhook_url", "")
        self._channel = config.get("channel", "#alerts")

    def notify(self, alert: Alert) -> None:
        color = (
            "danger" if alert.severity.value in ("critical", "error")
            else "warning" if alert.severity.value == "warn"
            else "good"
        )
        payload = {
            "channel": self._channel,
            "attachments": [
                {
                    "color": color,
                    "title": alert.name,
                    "text": alert.message,
                    "fields": [
                        {"title": "Severity", "value": alert.severity.value, "short": True},
                        {"title": "Value", "value": str(round(alert.value, 2)), "short": True},
                        {"title": "Status", "value": alert.status.value, "short": True},
                    ],
                }
            ],
        }
        self._post(payload)

    def _post(self, payload: dict[str, Any]) -> None:
        import urllib.request
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            self._webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        try:
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            logger = logging.getLogger("superdev.alerts")
            logger.error("Failed to send Slack alert: %s", e)


class WebhookAlertChannel(AlertNotifier):
    """Sends alert notifications via generic HTTP webhook."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._url = config.get("url", "")
        self._headers = config.get("headers", {})

    def notify(self, alert: Alert) -> None:
        import urllib.request
        payload = {
            "alert": alert.name,
            "severity": alert.severity.value,
            "status": alert.status.value,
            "message": alert.message,
            "value": alert.value,
            "threshold": alert.threshold,
            "labels": alert.labels,
        }
        data = json.dumps(payload).encode()
        headers = {"Content-Type": "application/json", **self._headers}
        req = urllib.request.Request(self._url, data=data, headers=headers)
        try:
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            logger = logging.getLogger("superdev.alerts")
            logger.error("Failed to send webhook alert: %s", e)
