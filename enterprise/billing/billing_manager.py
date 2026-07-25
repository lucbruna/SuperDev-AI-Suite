from __future__ import annotations as __

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import uuid4

from .subscription import Subscription, SubscriptionPlan
from .pricing import PRICING_PLANS, list_available_plans
from .invoicing import InvoiceManager


class BillingManager:
    def __init__(self) -> None:
        self._subscriptions: Dict[str, Subscription] = {}
        self._org_subscriptions: Dict[str, str] = {}
        self._invoice_manager = InvoiceManager()

    async def create_subscription(
        self, org_id: str, plan: str
    ) -> Subscription:
        await asyncio.sleep(0.01)
        plan_def = PRICING_PLANS.get(plan)
        if not plan_def:
            raise ValueError(f"Invalid plan: {plan}")

        existing = self._org_subscriptions.get(org_id)
        if existing:
            raise ValueError(f"Organization {org_id} already has a subscription")

        sub = Subscription(
            org_id=org_id,
            plan=SubscriptionPlan(tier=plan, label=plan_def["name"]),
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30),
            features=list(plan_def["features"]),
            limits={
                "max_users": plan_def["max_users"],
                "max_projects": plan_def["max_projects"],
                "max_agents": plan_def["max_agents"],
                "storage_gb": plan_def["storage_gb"],
                "api_calls_per_month": plan_def["api_calls_per_month"],
            },
            trial_end=datetime.utcnow() + timedelta(days=14) if plan == "free" else None,
        )
        if plan != "free":
            sub.status = "trialing"

        self._subscriptions[sub.id] = sub
        self._org_subscriptions[org_id] = sub.id
        return sub

    async def cancel_subscription(self, sub_id: str) -> Subscription:
        await asyncio.sleep(0.01)
        sub = self._subscriptions.get(sub_id)
        if not sub:
            raise ValueError(f"Subscription not found: {sub_id}")
        sub.cancel()
        return sub

    async def get_subscription(self, org_id: str) -> Subscription | None:
        await asyncio.sleep(0.01)
        sub_id = self._org_subscriptions.get(org_id)
        if not sub_id:
            return None
        return self._subscriptions.get(sub_id)

    async def list_plans(self) -> List[Dict[str, Any]]:
        await asyncio.sleep(0.01)
        return list_available_plans()

    async def change_plan(self, sub_id: str, new_plan: str) -> Subscription:
        await asyncio.sleep(0.01)
        plan_def = PRICING_PLANS.get(new_plan)
        if not plan_def:
            raise ValueError(f"Invalid plan: {new_plan}")

        sub = self._subscriptions.get(sub_id)
        if not sub:
            raise ValueError(f"Subscription not found: {sub_id}")

        sub.change_plan(new_plan)
        sub.features = list(plan_def["features"])
        sub.limits = {
            "max_users": plan_def["max_users"],
            "max_projects": plan_def["max_projects"],
            "max_agents": plan_def["max_agents"],
            "storage_gb": plan_def["storage_gb"],
            "api_calls_per_month": plan_def["api_calls_per_month"],
        }
        return sub

    async def get_invoice_manager(self) -> InvoiceManager:
        await asyncio.sleep(0.01)
        return self._invoice_manager

    async def generate_invoice(
        self, sub_id: str, period: tuple[datetime, datetime]
    ) -> Any:
        sub = self._subscriptions.get(sub_id)
        if not sub:
            raise ValueError(f"Subscription not found: {sub_id}")
        return await self._invoice_manager.generate_invoice(sub_id, period, sub.org_id)
