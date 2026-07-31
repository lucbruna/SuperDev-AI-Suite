"""CX Engine — Core customer experience engine."""
from typing import Dict, Any, Optional, List
from datetime import datetime
from .cx_models import (
    Customer, CustomerProfile, Interaction, Ticket,
    Lead, Recommendation, SentimentType, CustomerStatus, CustomerTier,
)
from .cx_config import CXConfig


class CXEngine:
    def __init__(self, config: Optional[CXConfig] = None):
        self._config = config or CXConfig()
        self._customers: Dict[str, Customer] = {}
        self._profiles: Dict[str, CustomerProfile] = {}
        self._interactions: List[Interaction] = []
        self._tickets: List[Ticket] = []
        self._leads: List[Lead] = []
        self._recommendations: List[Recommendation] = []

    def add_customer(self, customer: Customer) -> Customer:
        self._customers[customer.customer_id] = customer
        return customer

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        return self._customers.get(customer_id)

    def update_customer(self, customer_id: str, updates: Dict[str, Any]) -> Optional[Customer]:
        c = self._customers.get(customer_id)
        if not c:
            return None
        for k, v in updates.items():
            if hasattr(c, k):
                setattr(c, k, v)
        c.updated_at = datetime.now()
        return c

    def search_customers(self, query: str) -> List[Customer]:
        q = query.lower()
        return [
            c for c in self._customers.values()
            if q in c.name.lower() or q in c.email.lower() or q in c.company.lower()
        ]

    def list_customers(self, status: Optional[CustomerStatus] = None, tier: Optional[CustomerTier] = None) -> List[Customer]:
        customers = list(self._customers.values())
        if status:
            customers = [c for c in customers if c.status == status]
        if tier:
            customers = [c for c in customers if c.tier == tier]
        return customers

    def add_interaction(self, interaction: Interaction) -> Interaction:
        self._interactions.append(interaction)
        return interaction

    def get_customer_interactions(self, customer_id: str) -> List[Interaction]:
        return [i for i in self._interactions if i.customer_id == customer_id]

    def add_ticket(self, ticket: Ticket) -> Ticket:
        self._tickets.append(ticket)
        return ticket

    def get_tickets(self, status: Optional[str] = None) -> List[Ticket]:
        tickets = self._tickets
        if status:
            tickets = [t for t in tickets if t.status.value == status]
        return tickets

    def add_lead(self, lead: Lead) -> Lead:
        self._leads.append(lead)
        return lead

    def get_leads(self, status: Optional[str] = None) -> List[Lead]:
        leads = self._leads
        if status:
            leads = [l for l in leads if l.status.value == status]
        return leads

    def add_recommendation(self, rec: Recommendation) -> Recommendation:
        self._recommendations.append(rec)
        return rec

    def get_recommendations(self, customer_id: str) -> List[Recommendation]:
        return [r for r in self._recommendations if r.customer_id == customer_id]

    def get_stats(self) -> Dict[str, Any]:
        return {
            "customers": len(self._customers),
            "interactions": len(self._interactions),
            "tickets": len(self._tickets),
            "leads": len(self._leads),
            "recommendations": len(self._recommendations),
        }
