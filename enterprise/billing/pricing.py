from __future__ import annotations as __

from typing import Dict, List, Any
from pydantic import BaseModel


class PlanFeatures(BaseModel):
    max_users: int
    max_projects: int
    max_agents: int
    storage_gb: int
    api_calls_per_month: int
    features: List[str]


PRICING_PLANS: Dict[str, Dict[str, Any]] = {
    "free": {
        "name": "Free",
        "price": 0,
        "currency": "USD",
        "interval": "month",
        "max_users": 3,
        "max_projects": 5,
        "max_agents": 2,
        "storage_gb": 1,
        "api_calls_per_month": 1000,
        "features": [
            "Basic analytics",
            "Community support",
            "1 integration",
            "Public projects only",
        ],
    },
    "starter": {
        "name": "Starter",
        "price": 29,
        "currency": "USD",
        "interval": "month",
        "max_users": 10,
        "max_projects": 20,
        "max_agents": 5,
        "storage_gb": 10,
        "api_calls_per_month": 10000,
        "features": [
            "Advanced analytics",
            "Email support",
            "5 integrations",
            "Private projects",
            "API access",
            "Basic automation",
        ],
    },
    "pro": {
        "name": "Pro",
        "price": 99,
        "currency": "USD",
        "interval": "month",
        "max_users": 50,
        "max_projects": 100,
        "max_agents": 20,
        "storage_gb": 100,
        "api_calls_per_month": 100000,
        "features": [
            "Real-time analytics",
            "Priority support",
            "Unlimited integrations",
            "Custom automation",
            "Advanced permissions",
            "Audit logs",
            "SAML/SSO",
            "Webhooks",
        ],
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 499,
        "currency": "USD",
        "interval": "month",
        "max_users": 999,
        "max_projects": 999,
        "max_agents": 999,
        "storage_gb": 999,
        "api_calls_per_month": 9999999,
        "features": [
            "White-label",
            "Dedicated support",
            "Custom contracts",
            "On-premise option",
            "Compliance reports",
            "Custom SLA",
            "Advanced security",
            "Data retention controls",
            "Multi-region deployment",
            "Enterprise SSO",
        ],
    },
}


def get_plan(plan_tier: str) -> Dict[str, Any] | None:
    return PRICING_PLANS.get(plan_tier)


def list_available_plans() -> List[Dict[str, Any]]:
    return [{"tier": tier, **details} for tier, details in PRICING_PLANS.items()]
