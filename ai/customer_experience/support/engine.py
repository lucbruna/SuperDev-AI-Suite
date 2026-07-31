"""Support engine."""

from datetime import datetime

from .models import (
    ChatMessage,
    Escalation,
    KnowledgeArticle,
    SupportTicket,
    TicketPriority,
    TicketStatus,
)


class SupportEngine:
    def __init__(self):
        self._tickets: dict[str, SupportTicket] = {}
        self._messages: dict[str, list[ChatMessage]] = {}
        self._articles: dict[str, KnowledgeArticle] = {}
        self._escalations: list[Escalation] = []

    def create_ticket(self, ticket: SupportTicket) -> SupportTicket:
        self._tickets[ticket.ticket_id] = ticket
        return ticket

    def get_ticket(self, ticket_id: str) -> SupportTicket | None:
        return self._tickets.get(ticket_id)

    def update_ticket_status(self, ticket_id: str, status: TicketStatus) -> bool:
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            return False
        ticket.status = status
        ticket.updated_at = datetime.now()
        return True

    def resolve_ticket(self, ticket_id: str, resolution: str) -> bool:
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            return False
        ticket.status = TicketStatus.RESOLVED
        ticket.resolution = resolution
        ticket.updated_at = datetime.now()
        return True

    def get_tickets(
        self, status: TicketStatus | None = None, priority: TicketPriority | None = None
    ) -> list[SupportTicket]:
        tickets = list(self._tickets.values())
        if status:
            tickets = [t for t in tickets if t.status == status]
        if priority:
            tickets = [t for t in tickets if t.priority == priority]
        return tickets

    def add_chat_message(self, message: ChatMessage) -> ChatMessage:
        self._messages.setdefault(message.session_id, []).append(message)
        return message

    def get_chat_history(self, session_id: str) -> list[ChatMessage]:
        return self._messages.get(session_id, [])

    def add_knowledge_article(self, article: KnowledgeArticle) -> KnowledgeArticle:
        self._articles[article.article_id] = article
        return article

    def search_knowledge(self, query: str) -> list[KnowledgeArticle]:
        q = query.lower()
        return [
            a
            for a in self._articles.values()
            if q in a.title.lower() or q in a.content.lower() or q in [t.lower() for t in a.tags]
        ]

    def create_escalation(self, escalation: Escalation) -> Escalation:
        self._escalations.append(escalation)
        return escalation

    def get_escalations(self, ticket_id: str | None = None) -> list[Escalation]:
        if ticket_id:
            return [e for e in self._escalations if e.ticket_id == ticket_id]
        return list(self._escalations)

    def get_stats(self) -> dict:
        tickets = list(self._tickets.values())
        open_t = [t for t in tickets if t.status == TicketStatus.OPEN]
        resolved = [t for t in tickets if t.status == TicketStatus.RESOLVED]
        return {
            "total_tickets": len(tickets),
            "open_tickets": len(open_t),
            "resolved_tickets": len(resolved),
            "articles": len(self._articles),
            "escalations": len(self._escalations),
        }
