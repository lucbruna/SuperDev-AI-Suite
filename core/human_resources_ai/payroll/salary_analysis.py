"""
Salary Analysis - Analyze salary data against market benchmarks.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..employee_context import EmployeeContext
from ..hr_events import HREventBus
from ..hr_config import HRConfig

logger = logging.getLogger(__name__)


class SalaryAnalysis:
    def __init__(self, config: HRConfig, context: EmployeeContext, event_bus: HREventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    def analyze_position(self, position: str) -> Dict[str, Any]:
        return {
            "position": position,
            "market_average": 9000.0,
            "market_min": 6500.0,
            "market_max": 12000.0,
            "company_average": 8500.0,
            "competitiveness_percent": 94.4,
            "adjustment_recommended": 0.0,
        }

    def compare_to_market(self, position: str, current_salary: float) -> Dict[str, Any]:
        return {
            "position": position,
            "current_salary": current_salary,
            "market_p25": 7500.0,
            "market_p50": 9000.0,
            "market_p75": 11000.0,
            "positioning": "below_market" if current_salary < 9000.0 else "at_market" if current_salary < 11000.0 else "above_market",
        }
