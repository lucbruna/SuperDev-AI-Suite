"""ERP Config — Configuration for ERP operations."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ERPConfig:
    enabled: bool = True
    company_name: str = ""
    currency: str = "USD"
    tax_rate: float = 0.0
    low_stock_threshold: int = 10
    auto_reorder: bool = True
    approval_required_above: float = 50000.0
    default_payment_terms: int = 30
    warehouse_count: int = 1
    departments: list[str] = field(
        default_factory=lambda: ["sales", "purchasing", "warehouse", "production", "logistics", "hr", "finance"]
    )
    custom_settings: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.custom_settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.custom_settings[key] = value
