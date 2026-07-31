"""CX Factory — Factory for creating CX components."""
from typing import Dict, Any, Optional, List
from .cx_models import (
    Customer, CustomerProfile, Interaction, Ticket,
    Lead, Recommendation, CustomerStatus, CustomerTier,
    InteractionType, TicketPriority, TicketStatus, LeadStatus, SentimentType,
)


class CXFactory:
    def __init__(self):
        self._templates: Dict[str, Dict[str, Any]] = {
            "vip_customer": {"tier": CustomerTier.PLATINUM, "status": CustomerStatus.ACTIVE},
            "enterprise_customer": {"tier": CustomerTier.DIAMOND, "status": CustomerStatus.ACTIVE, "tags": ["enterprise"]},
            "trial_customer": {"tier": CustomerTier.BRONZE, "status": CustomerStatus.PROSPECT, "tags": ["trial"]},
            "at_risk_customer": {"tier": CustomerTier.SILVER, "status": CustomerStatus.ACTIVE, "tags": ["at_risk"]},
        }

    def create_customer(self, name: str, email: str = "", **kwargs) -> Customer:
        return Customer(name=name, email=email, **kwargs)

    def create_customer_from_template(self, template_name: str, name: str, email: str = "", **overrides) -> Customer:
        template = self._templates.get(template_name, {})
        params = {**template, "name": name, "email": email, **overrides}
        return Customer(**params)

    def create_interaction(self, customer_id: str, interaction_type: InteractionType = InteractionType.EMAIL, **kwargs) -> Interaction:
        return Interaction(customer_id=customer_id, interaction_type=interaction_type, **kwargs)

    def create_ticket(self, customer_id: str, subject: str, priority: TicketPriority = TicketPriority.MEDIUM, **kwargs) -> Ticket:
        return Ticket(customer_id=customer_id, subject=subject, priority=priority, **kwargs)

    def create_lead(self, name: str, email: str = "", source: str = "", **kwargs) -> Lead:
        return Lead(name=name, email=email, source=source, **kwargs)

    def create_recommendation(self, customer_id: str, item_id: str, item_name: str, score: float = 0.0, **kwargs) -> Recommendation:
        return Recommendation(customer_id=customer_id, item_id=item_id, item_name=item_name, score=score, **kwargs)

    def create_profile(self, customer_id: str, **kwargs) -> CustomerProfile:
        return CustomerProfile(customer_id=customer_id, **kwargs)

    def register_template(self, name: str, template: Dict[str, Any]) -> None:
        self._templates[name] = template

    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        return self._templates.get(name)

    def list_templates(self) -> List[str]:
        return list(self._templates.keys())
