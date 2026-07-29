"""
Benefits Manager - Manage employee benefits and compensation packages.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..employee_context import EmployeeContext
from ..hr_events import HREvent, HREventBus, EventType
from ..hr_models import Benefit
from ..hr_config import HRConfig

logger = logging.getLogger(__name__)


class BenefitsManager:
    def __init__(self, config: HRConfig, context: EmployeeContext, event_bus: HREventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    def get_benefits(self, employee_id: str) -> List[Benefit]:
        return [
            Benefit(id="B-001", name="Health Insurance", type="health", cost_per_employee=500.0, employer_contribution=400.0, employee_contribution=100.0),
            Benefit(id="B-002", name="Dental Insurance", type="dental", cost_per_employee=100.0, employer_contribution=80.0, employee_contribution=20.0),
            Benefit(id="B-003", name="Meal Voucher", type="meal", cost_per_employee=300.0, employer_contribution=300.0, employee_contribution=0.0),
        ]

    def calculate_total_cost(self, employee_id: str) -> float:
        return 800.0

    def enroll_in_benefit(self, employee_id: str, benefit_id: str) -> Dict[str, Any]:
        return {"employee_id": employee_id, "benefit_id": benefit_id, "status": "enrolled"}
