"""
Supply Chain Manager - High-level supply chain operations manager.

Provides a simplified interface for common supply chain operations
and coordinates between the engine and external systems.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .supply_chain_engine import SupplyChainEngine, EngineConfig
from .supply_context import SupplyChainContext
from .supply_events import SupplyChainEventBus
from .supply_models import (
    DemandForecast,
    InventoryItem,
    InventorySnapshot,
    LogisticsPlan,
    OptimizationResult,
    ProcurementOrder,
    ProcurementPlan,
    Supplier,
    SupplierEvaluation,
    WarehouseLayout,
)
from .supply_config import SupplyChainConfig
from .supply_security import SupplySecurityManager

logger = logging.getLogger(__name__)


@dataclass
class ManagerConfig:
    """Configuration for the Supply Chain Manager."""
    engine_config: EngineConfig
    enable_erp_integration: bool = True
    enable_financial_integration: bool = True
    enable_customer_ai_integration: bool = True
    enable_robotics_integration: bool = False
    decision_center_webhook: Optional[str] = None


class SupplyChainManager:
    """
    High-level Supply Chain Manager.
    
    Provides simplified API for:
    - Inventory management
    - Demand planning
    - Procurement operations
    - Supplier management
    - Logistics coordination
    - Warehouse operations
    - Strategic optimization
    """
    
    def __init__(self, config: ManagerConfig):
        self.config = config
        self.engine = SupplyChainEngine(config.engine_config)
        self.context = config.engine_config.context
        self.event_bus = config.engine_config.event_bus
        self.security = SupplySecurityManager()
        self._initialized = False
        
    async def initialize(self) -> None:
        """Initialize the manager and engine."""
        if self._initialized:
            return
            
        await self.engine.initialize()
        await self.engine.start()
        self._initialized = True
        logger.info("Supply Chain Manager initialized")
        
    async def shutdown(self) -> None:
        """Shutdown the manager and engine."""
        await self.engine.stop()
        self._initialized = False
        logger.info("Supply Chain Manager shutdown")
        
    # Inventory Operations
    
    async def get_inventory_level(self, product_id: str) -> int:
        """Get current inventory level for a product."""
        snapshot = await self.engine.get_inventory_status()
        return snapshot.get_product_quantity(product_id)
        
    async def get_inventory_snapshot(self) -> InventorySnapshot:
        """Get complete inventory snapshot."""
        return await self.engine.get_inventory_status()
        
    async def get_low_stock_items(self, threshold_days: int = 7) -> List[InventoryItem]:
        """Get items with stock below threshold."""
        return await self.context.inventory.get_low_stock(threshold_days)
        
    async def reserve_inventory(self, product_id: str, quantity: int, order_id: str) -> bool:
        """Reserve inventory for an order."""
        return await self.context.inventory.reserve(product_id, quantity, order_id)
        
    async def release_inventory(self, product_id: str, quantity: int, order_id: str) -> bool:
        """Release reserved inventory."""
        return await self.context.inventory.release(product_id, quantity, order_id)
        
    # Demand Operations
    
    async def get_demand_forecast(self, horizon_days: int = 30) -> DemandForecast:
        """Get demand forecast."""
        return await self.engine.get_demand_forecast(horizon_days)
        
    async def get_product_forecast(self, product_id: str, horizon_days: int = 30) -> Dict[str, Any]:
        """Get demand forecast for specific product."""
        forecast = await self.engine.get_demand_forecast(horizon_days)
        return forecast.get_product_forecast(product_id)
        
    async def analyze_seasonality(self, product_id: str) -> Dict[str, Any]:
        """Analyze seasonality patterns for a product."""
        return await self.context.demand.analyze_seasonality(product_id)
        
    async def analyze_market_trends(self, category: str) -> Dict[str, Any]:
        """Analyze market trends for a category."""
        return await self.context.demand.analyze_market_trends(category)
        
    # Procurement Operations
    
    async def create_purchase_order(self, order: ProcurementOrder) -> ProcurementOrder:
        """Create a purchase order."""
        return await self.context.procurement.create_order(order)
        
    async def get_procurement_plan(self, horizon_days: int = 30) -> ProcurementPlan:
        """Get procurement plan."""
        return await self.engine.get_procurement_plan(horizon_days)
        
    async def get_pending_orders(self) -> List[ProcurementOrder]:
        """Get all pending purchase orders."""
        return await self.context.procurement.get_pending_orders()
        
    async def approve_order(self, order_id: str, approver: str) -> bool:
        """Approve a purchase order."""
        return await self.context.procurement.approve(order_id, approver)
        
    async def reject_order(self, order_id: str, reason: str) -> bool:
        """Reject a purchase order."""
        return await self.context.procurement.reject(order_id, reason)
        
    async def get_price_analysis(self, product_id: str) -> Dict[str, Any]:
        """Get price analysis for a product."""
        return await self.context.procurement.analyze_prices(product_id)
        
    # Supplier Operations
    
    async def get_supplier(self, supplier_id: str) -> Optional[Supplier]:
        """Get supplier by ID."""
        return await self.context.suppliers.get(supplier_id)
        
    async def get_all_suppliers(self) -> List[Supplier]:
        """Get all suppliers."""
        return await self.context.suppliers.get_all()
        
    async def get_supplier_evaluations(self) -> List[SupplierEvaluation]:
        """Get all supplier evaluations."""
        return await self.engine.get_supplier_evaluations()
        
    async def evaluate_supplier(self, supplier_id: str) -> SupplierEvaluation:
        """Evaluate a specific supplier."""
        return await self.context.suppliers.evaluate(supplier_id)
        
    async def get_supplier_risk(self, supplier_id: str) -> Dict[str, Any]:
        """Get risk assessment for a supplier."""
        return await self.context.suppliers.assess_risk(supplier_id)
        
    async def find_alternative_suppliers(self, product_id: str, exclude: List[str] = None) -> List[Supplier]:
        """Find alternative suppliers for a product."""
        return await self.context.suppliers.find_alternatives(product_id, exclude)
        
    # Logistics Operations
    
    async def get_logistics_plan(self) -> LogisticsPlan:
        """Get current logistics plan."""
        return await self.engine.get_logistics_plan()
        
    async def optimize_routes(self, deliveries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize delivery routes."""
        return await self.context.logistics.optimize_routes(deliveries)
        
    async def get_delivery_prediction(self, order_id: str) -> Dict[str, Any]:
        """Get delivery prediction for an order."""
        return await self.context.logistics.predict_delivery(order_id)
        
    async def track_shipment(self, shipment_id: str) -> Dict[str, Any]:
        """Track a shipment."""
        return await self.context.logistics.track(shipment_id)
        
    # Warehouse Operations
    
    async def get_warehouse_layout(self) -> WarehouseLayout:
        """Get current warehouse layout."""
        return await self.engine.get_warehouse_layout()
        
    async def optimize_warehouse_layout(self) -> WarehouseLayout:
        """Optimize warehouse layout."""
        return await self.context.warehouse.optimize_layout()
        
    async def get_picking_route(self, order_id: str) -> List[Dict[str, Any]]:
        """Get optimized picking route for an order."""
        return await self.context.warehouse.get_picking_route(order_id)
        
    async def get_location_recommendations(self) -> List[Dict[str, Any]]:
        """Get product location recommendations."""
        return await self.context.warehouse.get_location_recommendations()
        
    # Forecasting & Planning
    
    async def run_capacity_planning(self, horizon_days: int = 90) -> Dict[str, Any]:
        """Run capacity planning simulation."""
        return await self.context.forecasting.plan_capacity(horizon_days)
        
    async def predict_risks(self, horizon_days: int = 30) -> List[Dict[str, Any]]:
        """Predict supply chain risks."""
        return await self.context.forecasting.predict_risks(horizon_days)
        
    async def simulate_demand_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate demand scenario."""
        return await self.engine.simulate_scenario(scenario)
        
    # Optimization
    
    async def run_global_optimization(self, scenario: Optional[Dict] = None) -> OptimizationResult:
        """Run global supply chain optimization."""
        return await self.engine.run_optimization(scenario)
        
    async def optimize_costs(self) -> Dict[str, Any]:
        """Run cost optimization."""
        return await self.context.optimization.optimize_costs()
        
    async def optimize_efficiency(self) -> Dict[str, Any]:
        """Run efficiency optimization."""
        return await self.context.optimization.optimize_efficiency()
        
    async def simulate_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate a what-if scenario using digital twin."""
        return await self.engine.simulate_scenario(scenario)
        
    # Analytics & KPIs
    
    async def get_kpis(self) -> Dict[str, float]:
        """Get current supply chain KPIs."""
        return await self.engine.get_kpis()
        
    async def get_inventory_kpis(self) -> Dict[str, float]:
        """Get inventory-specific KPIs."""
        return await self.context.metrics.calculate_inventory_kpis()
        
    async def get_procurement_kpis(self) -> Dict[str, float]:
        """Get procurement-specific KPIs."""
        return await self.context.metrics.calculate_procurement_kpis()
        
    async def get_logistics_kpis(self) -> Dict[str, float]:
        """Get logistics-specific KPIs."""
        return await self.context.metrics.calculate_logistics_kpis()
        
    async def get_supplier_kpis(self) -> Dict[str, float]:
        """Get supplier-specific KPIs."""
        return await self.context.metrics.calculate_supplier_kpis()
        
    # Autonomous Operations
    
    async def enable_autonomous_mode(self) -> None:
        """Enable autonomous decision making."""
        self.config.engine_config.enable_autonomous_mode = True
        logger.info("Autonomous mode enabled")
        
    async def disable_autonomous_mode(self) -> None:
        """Disable autonomous decision making."""
        self.config.engine_config.enable_autonomous_mode = False
        logger.info("Autonomous mode disabled")
        
    async def trigger_replenishment_check(self) -> List[ProcurementOrder]:
        """Manually trigger replenishment check."""
        return await self.context.inventory.check_and_replenish()
        
    async def emergency_reorder(self, product_id: str, quantity: int) -> ProcurementOrder:
        """Create emergency reorder."""
        return await self.context.procurement.emergency_order(product_id, quantity)
        
    # Integration Methods
    
    async def sync_with_erp(self) -> Dict[str, Any]:
        """Sync data with ERP system."""
        if not self.config.enable_erp_integration:
            return {"status": "disabled"}
        return await self.context.integrations.sync_erp()
        
    async def sync_with_financial(self) -> Dict[str, Any]:
        """Sync with financial AI module."""
        if not self.config.enable_financial_integration:
            return {"status": "disabled"}
        return await self.context.integrations.sync_financial()
        
    async def sync_with_customer_ai(self) -> Dict[str, Any]:
        """Sync with customer AI module."""
        if not self.config.enable_customer_ai_integration:
            return {"status": "disabled"}
        return await self.context.integrations.sync_customer_ai()
        
    async def sync_with_robotics(self) -> Dict[str, Any]:
        """Sync with robotics AI module."""
        if not self.config.enable_robotics_integration:
            return {"status": "disabled"}
        return await self.context.integrations.sync_robotics()
        
    async def send_to_decision_center(self, data: Dict[str, Any]) -> bool:
        """Send strategic data to decision center."""
        if not self.config.decision_center_webhook:
            return False
        return await self.context.integrations.send_decision_center(data)
        
    # Security
    
    def check_access(self, user_id: str, resource: str, action: str) -> bool:
        """Check if user has access to resource."""
        return self.security.check_access(user_id, resource, action)
        
    def encrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive supply chain data."""
        return self.security.encrypt(data)
        
    def decrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive supply chain data."""
        return self.security.decrypt(data)
        
    def audit_transaction(self, transaction: Dict[str, Any]) -> None:
        """Audit a supply chain transaction."""
        self.security.audit(transaction)
        
    # Status & Monitoring
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get engine status."""
        metrics = self.engine.get_metrics()
        return {
            "state": metrics.state.value,
            "uptime": (datetime.utcnow() - metrics.start_time).total_seconds() if metrics.start_time else 0,
            "decisions_made": metrics.decisions_made,
            "optimizations_run": metrics.optimizations_run,
            "predictions_made": metrics.predictions_made,
            "replenishments_triggered": metrics.replenishments_triggered,
            "alerts_generated": metrics.alerts_generated,
            "errors": metrics.errors,
            "subsystems": metrics.subsystem_status,
        }
        
    def is_healthy(self) -> bool:
        """Check if system is healthy."""
        metrics = self.engine.get_metrics()
        return metrics.state.value == "running" and metrics.errors < 10