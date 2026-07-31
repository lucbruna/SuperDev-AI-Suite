"""Recommendation engine."""

import uuid
from datetime import datetime, timedelta

from .models import (
    ContentRecommendation,
    Offer,
    ProductRecommendation,
    RecommendationStatus,
)


class RecommendationEngine:
    def __init__(self):
        self._product_recs: dict[str, list[ProductRecommendation]] = {}
        self._content_recs: dict[str, list[ContentRecommendation]] = {}
        self._offers: dict[str, list[Offer]] = {}

    def recommend_products(self, customer_id: str, context: dict | None = None) -> list[ProductRecommendation]:
        recs = []
        for i in range(3):
            rec = ProductRecommendation(
                recommendation_id=str(uuid.uuid4())[:8],
                customer_id=customer_id,
                product_id=f"prod_{i}",
                product_name=f"Recommended Product {i + 1}",
                score=0.9 - i * 0.1,
                reason="Based on purchase history",
            )
            recs.append(rec)
        self._product_recs.setdefault(customer_id, []).extend(recs)
        return recs

    def recommend_content(self, customer_id: str) -> list[ContentRecommendation]:
        recs = []
        for i in range(2):
            rec = ContentRecommendation(
                recommendation_id=str(uuid.uuid4())[:8],
                customer_id=customer_id,
                content_id=f"content_{i}",
                content_title=f"Article {i + 1}",
                content_type="article",
                score=0.85 - i * 0.1,
                reason="Based on interests",
            )
            recs.append(rec)
        self._content_recs.setdefault(customer_id, []).extend(recs)
        return recs

    def generate_offer(self, customer_id: str, discount: float = 10.0) -> Offer:
        offer = Offer(
            offer_id=str(uuid.uuid4())[:8],
            customer_id=customer_id,
            offer_type="discount",
            discount_percent=discount,
            description=f"{discount}% off your next purchase",
            valid_until=datetime.now() + timedelta(days=30),
        )
        self._offers.setdefault(customer_id, []).append(offer)
        return offer

    def accept_recommendation(self, recommendation_id: str) -> bool:
        for recs in self._product_recs.values():
            for rec in recs:
                if rec.recommendation_id == recommendation_id:
                    rec.status = RecommendationStatus.ACCEPTED
                    return True
        return False

    def get_customer_recommendations(self, customer_id: str) -> list[ProductRecommendation]:
        return self._product_recs.get(customer_id, [])

    def get_customer_offers(self, customer_id: str) -> list[Offer]:
        return self._offers.get(customer_id, [])

    def get_stats(self) -> dict:
        total_recs = sum(len(v) for v in self._product_recs.values())
        total_offers = sum(len(v) for v in self._offers.values())
        return {"total_recommendations": total_recs, "total_offers": total_offers}
