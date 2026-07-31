"""Communication subsystem facade (Volume 31)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.communication.agent_chat import AgentChat
from agent_orchestration.communication.event_router import EventRouter
from agent_orchestration.communication.message_bus import MessageBus
from agent_orchestration.communication.protocol_manager import ProtocolManager
from agent_orchestration.orchestrator_events import (OrchestratorEvents,
                                                     OrchestratorEventType)
from agent_orchestration.orchestrator_metrics import OrchestratorMetrics
from agent_orchestration.orchestrator_models import (AgentMessage, MessageType)


class CommunicationEngine:
    """Facade over the message bus, chat, routing and protocols."""

    def __init__(self, bus: MessageBus | None = None,
                 router: EventRouter | None = None,
                 protocols: ProtocolManager | None = None,
                 events: OrchestratorEvents | None = None,
                 metrics: OrchestratorMetrics | None = None) -> None:
        self.bus = bus or MessageBus()
        self.router = router or EventRouter()
        self.protocols = protocols or ProtocolManager()
        self.events = events or OrchestratorEvents()
        self.metrics = metrics or OrchestratorMetrics()

    def send(self, sender_id: str, recipient_id: str, content: str = "",
             message_type: MessageType = MessageType.DIRECT,
             payload: dict[str, Any] | None = None) -> AgentMessage | None:
        if not self.protocols.validate(message_type, payload or {}):
            self.metrics.increment("ao.protocol_violations")
            return None
        message = self.bus.send(sender_id, recipient_id, content,
                                message_type, payload)
        self.metrics.increment("ao.messages")
        self.events.publish(OrchestratorEventType.MESSAGE_SENT,
                            {"message_id": message.message_id,
                             "sender_id": sender_id,
                             "recipient_id": recipient_id})
        self.router.route(OrchestratorEventType.MESSAGE_SENT,
                          {"message_id": message.message_id})
        return message

    def chat(self, first_id: str, second_id: str) -> AgentChat:
        return AgentChat(first_id, second_id, self.bus)

    def inbox(self, agent_id: str) -> list[AgentMessage]:
        return self.bus.inbox(agent_id)

    def history(self) -> list[AgentMessage]:
        return self.bus.history()

    def on(self, event_type, handler) -> None:
        self.router.on(event_type, handler)

    def stats(self) -> dict[str, Any]:
        return {
            "messages": self.bus.count(),
            "protocols": self.protocols.protocols(),
            "metrics": self.metrics.snapshot()["counters"],
        }
