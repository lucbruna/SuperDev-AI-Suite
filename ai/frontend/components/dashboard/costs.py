"""
Cost Dashboard
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class CostItem:
    service: str
    amount: float
    currency: str = "USD"
    period: str = "monthly"
    trend: float = 0.0


class CostDashboard:
    def __init__(self):
        self.items: List[CostItem] = []
        self.budget: float = 0
        self.currency: str = "USD"
        
    def add_item(self, item: CostItem) -> None:
        self.items.append(item)
        
    def get_total(self) -> float:
        return sum(item.amount for item in self.items)
        
    def get_budget_usage(self) -> float:
        if self.budget <= 0:
            return 0
        return (self.get_total() / self.budget) * 100
        
    def render(self) -> Dict[str, Any]:
        return {
            "items": [{"service": i.service, "amount": i.amount, "currency": i.currency} for i in self.items],
            "total": self.get_total(),
            "budget": self.budget,
            "budgetUsage": self.get_budget_usage(),
        }
