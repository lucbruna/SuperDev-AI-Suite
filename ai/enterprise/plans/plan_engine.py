"""Plan engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class PlanEngine:
    def __init__(self) -> None:
        self._plans: Dict[str, Dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def create(self, name: str, slug: str, price: float, currency: str = "BRL", billing_cycle: str = "monthly") -> Dict[str, Any]:
        plan = {"name": name, "slug": slug, "price": price, "currency": currency, "billing_cycle": billing_cycle, "features": {}, "limits": {}, "active": True, "created_at": time.time()}
        self._plans[slug] = plan
        return plan
    def get(self, slug: str) -> Optional[Dict[str, Any]]:
        return self._plans.get(slug)
    def update(self, slug: str, **kwargs: Any) -> Optional[Dict[str, Any]]:
        plan = self._plans.get(slug)
        if plan:
            plan.update(kwargs)
            return plan
        return None
    def delete(self, slug: str) -> bool:
        if slug in self._plans:
            del self._plans[slug]
            return True
        return False
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._plans.values())
    def list_active(self) -> List[Dict[str, Any]]:
        return [p for p in self._plans.values() if p.get("active")]
    def count(self) -> int:
        return len(self._plans)
