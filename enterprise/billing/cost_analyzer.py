from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any


class CostAnalyzer:
    def __init__(self):
        self._entries: list[dict[str, Any]] = []
        self._budgets: list[dict[str, Any]] = []

    def add_entry(self, project: str, agent: str, provider: str, model: str, cost: Decimal, tokens: int, timestamp: str | None = None):
        self._entries.append({
            "project": project, "agent": agent, "provider": provider, "model": model,
            "cost": cost, "tokens": tokens, "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
        })

    def by_project(self) -> dict[str, Decimal]:
        result: dict[str, Decimal] = {}
        for e in self._entries:
            result[e["project"]] = result.get(e["project"], Decimal("0")) + e["cost"]
        return result

    def by_provider(self) -> dict[str, Decimal]:
        result: dict[str, Decimal] = {}
        for e in self._entries:
            result[e["provider"]] = result.get(e["provider"], Decimal("0")) + e["cost"]
        return result

    def by_agent(self) -> dict[str, Decimal]:
        result: dict[str, Decimal] = {}
        for e in self._entries:
            result[e["agent"]] = result.get(e["agent"], Decimal("0")) + e["cost"]
        return result

    def by_day(self) -> dict[str, Decimal]:
        result: dict[str, Decimal] = {}
        for e in self._entries:
            day = e["timestamp"][:10]
            result[day] = result.get(day, Decimal("0")) + e["cost"]
        return dict(sorted(result.items()))

    def total_cost(self) -> Decimal:
        return sum((e["cost"] for e in self._entries), Decimal("0"))

    def total_tokens(self) -> int:
        return sum(e["tokens"] for e in self._entries)

    def avg_cost_per_1k_tokens(self) -> Decimal:
        tokens = self.total_tokens()
        if tokens == 0:
            return Decimal("0")
        return (self.total_cost() / Decimal(tokens)) * Decimal("1000")

    def summary(self) -> dict[str, Any]:
        return {
            "total_cost": str(self.total_cost()),
            "total_tokens": self.total_tokens(),
            "avg_cost_per_1k_tokens": str(self.avg_cost_per_1k_tokens().quantize(Decimal("0.0001"))),
            "projects": {k: str(v) for k, v in sorted(self.by_project().items(), key=lambda x: x[1], reverse=True)},
            "providers": {k: str(v) for k, v in sorted(self.by_provider().items(), key=lambda x: x[1], reverse=True)},
            "agents": {k: str(v) for k, v in sorted(self.by_agent().items(), key=lambda x: x[1], reverse=True)},
            "daily": {k: str(v) for k, v in self.by_day().items()},
        }


class BudgetManager:
    def __init__(self):
        self._budgets: list[dict[str, Any]] = []

    def set_budget(self, name: str, limit: Decimal, period: str = "monthly", scope: str = "global"):
        self._budgets.append({"name": name, "limit": limit, "period": period, "scope": scope, "spent": Decimal("0"), "alerts": []})

    def record_spend(self, scope: str, amount: Decimal):
        for b in self._budgets:
            if b["scope"] == scope or b["scope"] == "global":
                b["spent"] += amount
                pct = (b["spent"] / b["limit"]) * 100
                if pct >= 90 and "90%" not in [a["type"] for a in b["alerts"]]:
                    b["alerts"].append({"type": "90%", "message": f"Budget '{b['name']}' at {pct:.0f}% used", "timestamp": __import__("datetime").datetime.now().isoformat()})
                if pct >= 100 and "100%" not in [a["type"] for a in b["alerts"]]:
                    b["alerts"].append({"type": "100%", "message": f"Budget '{b['name']}' exceeded!", "timestamp": __import__("datetime").datetime.now().isoformat()})

    def budget_status(self) -> list[dict[str, Any]]:
        return [{"name": b["name"], "limit": str(b["limit"]), "spent": str(b["spent"]), "pct": round(float(b["spent"] / b["limit"]) * 100, 1) if b["limit"] > 0 else 0, "alerts": b["alerts"]} for b in self._budgets]


class CostForecast:
    def __init__(self):
        self._history: list[Decimal] = []

    def add_day(self, cost: Decimal):
        self._history.append(cost)

    def forecast(self, days: int = 30) -> dict[str, Any]:
        if not self._history:
            return {"forecast": [], "avg_daily": "0", "projected": "0"}
        avg = sum(self._history, Decimal("0")) / Decimal(len(self._history))
        projection = avg * Decimal(days)
        return {
            "avg_daily": str(avg.quantize(Decimal("0.01"))),
            "projected": str(projection.quantize(Decimal("0.01"))),
            "days_analyzed": len(self._history),
            "forecast_days": days,
        }