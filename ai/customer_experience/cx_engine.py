"""CX Engine — Core customer experience engine."""

from datetime import datetime
from typing import Any

from .cx_config import CXConfig
from .cx_models import (
    Customer,
    CustomerProfile,
    CustomerStatus,
    CustomerTier,
    Interaction,
    Lead,
    Recommendation,
    Ticket,
)


class CXEngine:
    def __init__(self, config: CXConfig | None = None):
        self._config = config or CXConfig()
        self._customers: dict[str, Customer] = {}
        self._profiles: dict[str, CustomerProfile] = {}
        self._interactions: list[Interaction] = []
        self._tickets: list[Ticket] = []
        self._leads: list[Lead] = []
        self._recommendations: list[Recommendation] = []

    def add_customer(self, customer: Customer) -> Customer:
        self._customers[customer.customer_id] = customer
        return customer

    def get_customer(self, customer_id: str) -> Customer | None:
        return self._customers.get(customer_id)

    def update_customer(self, customer_id: str, updates: dict[str, Any]) -> Customer | None:
        c = self._customers.get(customer_id)
        if not c:
            return None
        for k, v in updates.items():
            if hasattr(c, k):
                setattr(c, k, v)
        c.updated_at = datetime.now()
        return c

    def search_customers(self, query: str) -> list[Customer]:
        q = query.lower()
        return [
            c for c in self._customers.values() if q in c.name.lower() or q in c.email.lower() or q in c.company.lower()
        ]

    def list_customers(self, status: CustomerStatus | None = None, tier: CustomerTier | None = None) -> list[Customer]:
        customers = list(self._customers.values())
        if status:
            customers = [c for c in customers if c.status == status]
        if tier:
            customers = [c for c in customers if c.tier == tier]
        return customers

    def add_interaction(self, interaction: Interaction) -> Interaction:
        self._interactions.append(interaction)
        return interaction

    def get_customer_interactions(self, customer_id: str) -> list[Interaction]:
        return [i for i in self._interactions if i.customer_id == customer_id]

    def add_ticket(self, ticket: Ticket) -> Ticket:
        self._tickets.append(ticket)
        return ticket

    def get_tickets(self, status: str | None = None) -> list[Ticket]:
        tickets = self._tickets
        if status:
            tickets = [t for t in tickets if t.status.value == status]
        return tickets

    def add_lead(self, lead: Lead) -> Lead:
        self._leads.append(lead)
        return lead

    def get_leads(self, status: str | None = None) -> list[Lead]:
        leads = self._leads
        if status:
            leads = [l for l in leads if l.status.value == status]
        return leads

    def add_recommendation(self, rec: Recommendation) -> Recommendation:
        self._recommendations.append(rec)
        return rec

    def get_recommendations(self, customer_id: str) -> list[Recommendation]:
        return [r for r in self._recommendations if r.customer_id == customer_id]

    def get_stats(self) -> dict[str, Any]:
        return {
            "customers": len(self._customers),
            "interactions": len(self._interactions),
            "tickets": len(self._tickets),
            "leads": len(self._leads),
            "recommendations": len(self._recommendations),
        }
