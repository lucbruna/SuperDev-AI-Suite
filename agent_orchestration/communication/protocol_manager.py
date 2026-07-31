"""Communication protocol management (Volume 31)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.orchestrator_models import MessageType

# Message-level schema per type (used by describe).
_SUPPORTED = {
    MessageType.DIRECT: {"content", "payload"},
    MessageType.BROADCAST: {"content", "payload"},
    MessageType.REQUEST: {"content", "payload"},
    MessageType.RESPONSE: {"content", "payload"},
    MessageType.EVENT: {"event", "payload"},
}

# Required keys inside the payload per message type (used by validate).
_REQUIRED_PAYLOAD = {
    MessageType.EVENT: {"event"},
}


class ProtocolManager:
    """Validates messages against supported communication protocols."""

    def __init__(self) -> None:
        self._protocols: dict[str, dict[str, Any]] = {}

    def register_protocol(self, name: str, version: str = "1.0",
                          allowed_fields: list[str] | None = None) -> None:
        self._protocols[name] = {
            "version": version,
            "allowed_fields": list(allowed_fields or []),
        }

    def protocols(self) -> list[str]:
        return list(self._protocols)

    def validate(self, message_type: MessageType,
                 payload: dict[str, Any] | None) -> bool:
        required = _REQUIRED_PAYLOAD.get(message_type, set())
        return required.issubset(set(payload or {}))

    def message_supported(self, message_type: MessageType) -> bool:
        return message_type in _SUPPORTED

    def describe(self, message_type: MessageType) -> dict[str, Any]:
        return {"type": message_type.value,
                "fields": sorted(_SUPPORTED.get(message_type, set()))}
