"""Savings estimation (Volume 37, Fase 6)."""

from __future__ import annotations

from devops_engine.devops_protocols import rate


class SavingsCalculator:
    """Estimates savings from rightsizing and reserved instances."""

    def rightsizing_saving(self, cost_per_hour: float,
                           utilization: float,
                           target_utilization: float = 0.8) -> float:
        """Saving from downsizing an underused resource."""
        underuse = max(0.0, target_utilization - rate(utilization, 1.0))
        return round(cost_per_hour * (underuse / target_utilization), 2)

    def reserved_saving(self, amount: float,
                        discount: float = 0.3) -> float:
        """Saving from committing to reserved capacity."""
        return round(float(amount) * max(0.0, min(1.0, discount)), 2)
