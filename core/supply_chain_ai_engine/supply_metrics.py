"""
Supply Chain Metrics - KPI calculations and performance metrics.

Provides comprehensive KPI tracking, metric calculations,
and performance analysis for all supply chain operations.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from .supply_context import SupplyChainContext

logger = logging.getLogger(__name__)


class MetricCategory(Enum):
    INVENTORY = "inventory"
    PROCUREMENT = "procurement"
    LOGISTICS = "logistics"
    SUPPLIER = "supplier"
    DEMAND = "demand"
    WAREHOUSE = "warehouse"
    FINANCIAL = "financial"
    OVERALL = "overall"


@dataclass
class MetricDefinition:
    """Definition of a single metric."""
    key: str
    name: str
    description: str
    category: MetricCategory
    unit: str
    higher_is_better: bool
    formula: Optional[str] = None
    threshold_good: Optional[float] = None
    threshold_warning: Optional[float] = None
    threshold_bad: Optional[float] = None


@dataclass
class MetricValue:
    """Value of a metric at a point in time."""
    key: str
    value: float
    timestamp: datetime
    category: MetricCategory
    unit: str
    status: str = "unknown"
    previous_value: Optional[float] = None
    change_percent: Optional[float] = None


class SupplyChainMetrics:
    """
    Central metrics repository for the Supply Chain AI Engine.
    
    Calculates, stores, and provides KPIs for all supply chain aspects.
    """
    
    def __init__(self, context: SupplyChainContext):
        self.context = context
        self._metric_definitions: Dict[str, MetricDefinition] = {}
        self._metric_history: Dict[str, List[MetricValue]] = {}
        self._max_history = 365
        self._calc_functions: Dict[str, Callable] = {}
        self._init_definitions()
        self._init_calculators()
        
    def _init_definitions(self) -> None:
        """Initialize all metric definitions."""
        definitions = [
            # Inventory Metrics
            MetricDefinition("inventory_turnover", "Inventory Turnover", "Rate at which inventory is sold/used", MetricCategory.INVENTORY, "turns/year", True, threshold_warning=4.0, threshold_bad=2.0),
            MetricDefinition("stockout_rate", "Stockout Rate", "Percentage of time items are out of stock", MetricCategory.INVENTORY, "%", False, threshold_good=1.0, threshold_warning=3.0),
            MetricDefinition("fill_rate", "Order Fill Rate", "Percentage of orders filled from stock", MetricCategory.INVENTORY, "%", True, threshold_good=98.0, threshold_warning=95.0),
            MetricDefinition("inventory_accuracy", "Inventory Accuracy", "Accuracy of inventory records vs physical", MetricCategory.INVENTORY, "%", True, threshold_good=99.0, threshold_warning=97.0),
            MetricDefinition("excess_inventory", "Excess Inventory Ratio", "Ratio of excess to optimal stock", MetricCategory.INVENTORY, "%", False, threshold_good=5.0, threshold_warning=15.0),
            MetricDefinition("days_on_hand", "Days on Hand", "Average days of inventory available", MetricCategory.INVENTORY, "days", False),
            
            # Procurement Metrics
            MetricDefinition("procurement_cycle_time", "Procurement Cycle Time", "Average time from order to receipt", MetricCategory.PROCUREMENT, "days", False),
            MetricDefinition("order_accuracy", "Order Accuracy", "Percentage of orders received correctly", MetricCategory.PROCUREMENT, "%", True, threshold_good=99.0, threshold_warning=97.0),
            MetricDefinition("cost_savings", "Procurement Cost Savings", "Cost savings achieved vs budget", MetricCategory.PROCUREMENT, "%", True),
            MetricDefinition("emergency_orders", "Emergency Orders Rate", "Percentage of emergency vs planned orders", MetricCategory.PROCUREMENT, "%", False, threshold_good=5.0, threshold_warning=10.0),
            
            # Logistics Metrics
            MetricDefinition("on_time_delivery", "On-Time Delivery Rate", "Percentage of deliveries on time", MetricCategory.LOGISTICS, "%", True, threshold_good=96.0, threshold_warning=90.0),
            MetricDefinition("logistics_cost", "Logistics Cost per Unit", "Average logistics cost per unit", MetricCategory.LOGISTICS, "$", False),
            MetricDefinition("delivery_accuracy", "Delivery Accuracy", "Percentage of correct deliveries", MetricCategory.LOGISTICS, "%", True, threshold_good=99.0, threshold_warning=97.0),
            MetricDefinition("route_efficiency", "Route Efficiency", "Average route optimization efficiency", MetricCategory.LOGISTICS, "%", True, threshold_good=85.0, threshold_warning=70.0),
            
            # Supplier Metrics
            MetricDefinition("supplier_on_time", "Supplier On-Time Rate", "Percentage of supplier deliveries on time", MetricCategory.SUPPLIER, "%", True, threshold_good=95.0, threshold_warning=90.0),
            MetricDefinition("supplier_quality", "Supplier Quality Rate", "Percentage of defect-free deliveries", MetricCategory.SUPPLIER, "%", True, threshold_good=98.0, threshold_warning=95.0),
            MetricDefinition("supplier_lead_time", "Supplier Lead Time", "Average lead time from suppliers", MetricCategory.SUPPLIER, "days", False),
            MetricDefinition("supplier_diversity", "Supplier Diversity Score", "Score based on supplier base diversity", MetricCategory.SUPPLIER, "score", True),
            
            # Demand Metrics
            MetricDefinition("forecast_accuracy", "Forecast Accuracy", "Accuracy of demand forecasts", MetricCategory.DEMAND, "%", True, threshold_good=85.0, threshold_warning=75.0),
            MetricDefinition("demand_volatility", "Demand Volatility", "Coefficient of demand variation", MetricCategory.DEMAND, "%", False),
            MetricDefinition("seasonal_impact", "Seasonality Impact", "Revenue impact from seasonality", MetricCategory.DEMAND, "%", True),
            
            # Warehouse Metrics
            MetricDefinition("warehouse_utilization", "Warehouse Utilization", "Percentage of warehouse capacity used", MetricCategory.WAREHOUSE, "%", False, threshold_good=85.0, threshold_warning=75.0),
            MetricDefinition("picking_accuracy", "Picking Accuracy", "Percentage of correct picks", MetricCategory.WAREHOUSE, "%", True, threshold_good=99.5, threshold_warning=99.0),
            MetricDefinition("picking_efficiency", "Picking Efficiency", "Items picked per hour", MetricCategory.WAREHOUSE, "items/hr", True),
            
            # Financial Metrics
            MetricDefinition("total_inventory_cost", "Total Inventory Cost", "Total cost of carrying inventory", MetricCategory.FINANCIAL, "$", False),
            MetricDefinition("supply_chain_cost", "Supply Chain Cost Ratio", "Supply chain cost as percentage of revenue", MetricCategory.FINANCIAL, "%", False),
            MetricDefinition("working_capital", "Working Capital Impact", "Working capital tied in supply chain", MetricCategory.FINANCIAL, "$", False),
            
            # Overall Metrics
            MetricDefinition("perfect_order_rate", "Perfect Order Rate", "Percentage of perfect orders end-to-end", MetricCategory.OVERALL, "%", True, threshold_good=96.0, threshold_warning=92.0),
            MetricDefinition("supply_chain_agility", "Supply Chain Agility", "Time to respond to demand changes", MetricCategory.OVERALL, "hours", True),
            MetricDefinition("overall_performance", "Overall SC Performance", "Aggregate supply chain performance score", MetricCategory.OVERALL, "score", True),
        ]
        
        for definition in definitions:
            self._metric_definitions[definition.key] = definition
            
    def _init_calculators(self) -> None:
        """Register calculation functions."""
        self._calc_functions["inventory_turnover"] = self._calc_inventory_turnover
        self._calc_functions["stockout_rate"] = self._calc_stockout_rate
        self._calc_functions["fill_rate"] = self._calc_fill_rate
        self._calc_functions["on_time_delivery"] = self._calc_on_time_delivery
        self._calc_functions["forecast_accuracy"] = self._calc_forecast_accuracy
        self._calc_functions["warehouse_utilization"] = self._calc_warehouse_utilization
        self._calc_functions["perfect_order_rate"] = self._calc_perfect_order_rate
        self._calc_functions["overall_performance"] = self._calc_overall_performance
        
    def get_definition(self, key: str) -> Optional[MetricDefinition]:
        return self._metric_definitions.get(key)
        
    def get_all_definitions(self) -> List[MetricDefinition]:
        return list(self._metric_definitions.values())
        
    def get_by_category(self, category: MetricCategory) -> List[MetricDefinition]:
        return [d for d in self._metric_definitions.values() if d.category == category]
        
    def record_value(self, key: str, value: float) -> MetricValue:
        """Record a metric value."""
        definition = self._metric_definitions.get(key)
        if not definition:
            raise ValueError(f"Unknown metric: {key}")
            
        history = self._metric_history.setdefault(key, [])
        previous = history[-1] if history else None
        
        metric_value = MetricValue(
            key=key,
            value=value,
            timestamp=datetime.utcnow(),
            category=definition.category,
            unit=definition.unit,
            status=self._evaluate_status(definition, value),
            previous_value=previous.value if previous else None,
            change_percent=self._calc_change(value, previous.value) if previous else None,
        )
        
        history.append(metric_value)
        if len(history) > self._max_history:
            history.pop(0)
            
        return metric_value
        
    def get_latest(self, key: str) -> Optional[MetricValue]:
        history = self._metric_history.get(key, [])
        return history[-1] if history else None
        
    def get_history(self, key: str, days: int = 30) -> List[MetricValue]:
        history = self._metric_history.get(key, [])
        cutoff = datetime.utcnow() - timedelta(days=days)
        return [m for m in history if m.timestamp >= cutoff]
        
    def get_all_latest(self) -> Dict[str, MetricValue]:
        result = {}
        for key in self._metric_definitions:
            latest = self.get_latest(key)
            if latest:
                result[key] = latest
        return result
        
    def get_category_latest(self, category: MetricCategory) -> Dict[str, MetricValue]:
        definitions = self.get_by_category(category)
        result = {}
        for definition in definitions:
            latest = self.get_latest(definition.key)
            if latest:
                result[definition.key] = latest
        return result
        
    def _evaluate_status(self, definition: MetricDefinition, value: float) -> str:
        if definition.higher_is_better:
            if definition.threshold_good is not None and value >= definition.threshold_good:
                return "good"
            if definition.threshold_warning is not None and value >= definition.threshold_warning:
                return "warning"
            return "bad"
        else:
            if definition.threshold_good is not None and value <= definition.threshold_good:
                return "good"
            if definition.threshold_warning is not None and value <= definition.threshold_warning:
                return "warning"
            return "bad"
            
    @staticmethod
    def _calc_change(value: float, previous: float) -> float:
        if previous == 0:
            return 0
        return ((value - previous) / previous) * 100
        
    async def _calc_inventory_turnover(self) -> float:
        return self.context.inventory.get("turnover", 6.0)
        
    async def _calc_stockout_rate(self) -> float:
        return self.context.inventory.get("stockout_rate", 2.0)
        
    async def _calc_fill_rate(self) -> float:
        return self.context.inventory.get("fill_rate", 97.0)
        
    async def _calc_on_time_delivery(self) -> float:
        return self.context.logistics.get("on_time_rate", 94.0)
        
    async def _calc_forecast_accuracy(self) -> float:
        return self.context.demand.get("forecast_accuracy", 82.0)
        
    async def _calc_warehouse_utilization(self) -> float:
        return self.context.warehouse.get("utilization", 78.0)
        
    async def _calc_perfect_order_rate(self) -> float:
        fill = await self._calc_fill_rate()
        on_time = await self._calc_on_time_delivery()
        accuracy = self.context.procurement.get("order_accuracy", 98.0)
        return fill * on_time * accuracy / 10000
        
    async def _calc_overall_performance(self) -> float:
        scores = []
        for key in ["inventory_turnover", "fill_rate", "on_time_delivery", "forecast_accuracy", "supplier_quality"]:
            latest = self.get_latest(key)
            if latest:
                scores.append(latest.value)
        return sum(scores) / len(scores) if scores else 0


class KPICalculator:
    """
    Strategic KPI Calculator.
    
    Provides pre-defined KPI dashboards and strategic
    performance indicators for decision support.
    """
    
    def __init__(self, context: SupplyChainContext):
        self.metrics = SupplyChainMetrics(context)
        self.context = context
        
    async def calculate_all(self) -> Dict[str, float]:
        """Calculate all available KPIs."""
        results = {}
        for key, func in self.metrics._calc_functions.items():
            try:
                results[key] = await func()
            except Exception as e:
                logger.error(f"Error calculating {key}: {e}")
                latest = self.metrics.get_latest(key)
                if latest:
                    results[key] = latest.value
        return results
        
    async def get_inventory_kpis(self) -> Dict[str, float]:
        kpi_keys = ["inventory_turnover", "stockout_rate", "fill_rate", "inventory_accuracy", "excess_inventory", "days_on_hand"]
        return {k: v for k, v in (await self.calculate_all()).items() if k in kpi_keys}
        
    async def get_procurement_kpis(self) -> Dict[str, float]:
        kpi_keys = ["procurement_cycle_time", "order_accuracy", "cost_savings", "emergency_orders"]
        return {k: v for k, v in (await self.calculate_all()).items() if k in kpi_keys}
        
    async def get_logistics_kpis(self) -> Dict[str, float]:
        kpi_keys = ["on_time_delivery", "logistics_cost", "delivery_accuracy", "route_efficiency"]
        return {k: v for k, v in (await self.calculate_all()).items() if k in kpi_keys}
        
    async def get_supplier_kpis(self) -> Dict[str, float]:
        kpi_keys = ["supplier_on_time", "supplier_quality", "supplier_lead_time", "supplier_diversity"]
        return {k: v for k, v in (await self.calculate_all()).items() if k in kpi_keys}
        
    async def get_financial_kpis(self) -> Dict[str, float]:
        kpi_keys = ["total_inventory_cost", "supply_chain_cost", "working_capital"]
        return {k: v for k, v in (await self.calculate_all()).items() if k in kpi_keys}
        
    async def get_strategic_kpis(self) -> Dict[str, float]:
        kpi_keys = ["perfect_order_rate", "supply_chain_agility", "overall_performance"]
        return {k: v for k, v in (await self.calculate_all()).items() if k in kpi_keys}