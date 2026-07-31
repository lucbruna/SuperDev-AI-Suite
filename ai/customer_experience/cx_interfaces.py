"""CX Interfaces — Protocol interfaces for customer experience."""

from abc import ABC, abstractmethod
from typing import Any

from .cx_models import (
    Customer,
    CustomerJourney,
    CustomerProfile,
    Lead,
    LoyaltyTransaction,
    Recommendation,
    Ticket,
)


class CRMEngineInterface(ABC):
    @abstractmethod
    def add_customer(self, customer: Customer) -> Customer:
        pass

    @abstractmethod
    def get_customer(self, customer_id: str) -> Customer | None:
        pass

    @abstractmethod
    def update_customer(self, customer_id: str, updates: dict[str, Any]) -> Customer | None:
        pass

    @abstractmethod
    def search_customers(self, query: str) -> list[Customer]:
        pass


class ProfileEngineInterface(ABC):
    @abstractmethod
    def build_profile(self, customer_id: str) -> CustomerProfile:
        pass

    @abstractmethod
    def get_profile(self, customer_id: str) -> CustomerProfile | None:
        pass

    @abstractmethod
    def update_profile(self, customer_id: str, updates: dict[str, Any]) -> CustomerProfile | None:
        pass


class SalesEngineInterface(ABC):
    @abstractmethod
    def score_lead(self, lead: Lead) -> Lead:
        pass

    @abstractmethod
    def predict_conversion(self, lead_id: str) -> float:
        pass

    @abstractmethod
    def get_leads(self, status: str | None = None) -> list[Lead]:
        pass


class SupportEngineInterface(ABC):
    @abstractmethod
    def create_ticket(self, ticket: Ticket) -> Ticket:
        pass

    @abstractmethod
    def resolve_ticket(self, ticket_id: str, resolution: str) -> bool:
        pass

    @abstractmethod
    def get_tickets(self, status: str | None = None) -> list[Ticket]:
        pass


class RecommendationEngineInterface(ABC):
    @abstractmethod
    def recommend(self, customer_id: str, context: dict | None = None) -> list[Recommendation]:
        pass

    @abstractmethod
    def record_acceptance(self, recommendation_id: str) -> bool:
        pass


class SentimentEngineInterface(ABC):
    @abstractmethod
    def analyze(self, text: str) -> dict[str, Any]:
        pass

    @abstractmethod
    def get_customer_sentiment(self, customer_id: str) -> dict[str, Any]:
        pass


class LoyaltyEngineInterface(ABC):
    @abstractmethod
    def earn_points(self, customer_id: str, points: int, description: str) -> LoyaltyTransaction:
        pass

    @abstractmethod
    def redeem_points(self, customer_id: str, points: int, description: str) -> LoyaltyTransaction:
        pass

    @abstractmethod
    def get_balance(self, customer_id: str) -> int:
        pass


class JourneyEngineInterface(ABC):
    @abstractmethod
    def start_journey(self, customer_id: str) -> CustomerJourney:
        pass

    @abstractmethod
    def advance_stage(self, journey_id: str, stage: str) -> bool:
        pass

    @abstractmethod
    def get_journey(self, customer_id: str) -> CustomerJourney | None:
        pass
