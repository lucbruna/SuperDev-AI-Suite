"""
Supply Chain AI Engine - Core Engine

Central intelligence engine that orchestrates all supply chain AI subsystems.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from .supply_context import SupplyChainContext
from .supply_events import SupplyChainEvent, SupplyChainEventBus, EventType
from .supply_models import (
    DemandForecast,
    InventorySnapshot,
    LogisticsPlan,
    OptimizationResult,
    ProcurementPlan,
    SupplierEvaluation,
    WarehouseLayout,
)
from .supply_config import SupplyChainConfig

logger = logging.getLogger(__name__)


class EngineState(Enum):
    """Supply Chain Engine operational states."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class EngineConfig:
    """Configuration for the Supply Chain Engine."""
    config: SupplyChainConfig
    event_bus: SupplyChainEventBus
    context: SupplyChainContext
    auto_replenishment: bool = True
    forecasting_enabled: bool = True
    optimization_enabled: bool = True
    auto_approval_threshold: float = 10000.0
    max_concurrent_optimizations: int = 5
    decision_interval_seconds: int = 300
    enable_autonomous_mode: bool = False


@dataclass
class EngineMetrics:
    """Runtime metrics for the engine."""
    state: EngineState = EngineState.INITIALIZING
    start_time: Optional[datetime] = None
    decisions_made: int = 0
    optimizations_run: int = 0
    predictions_made: int = 0
    replenishments_triggered: int = 0
    alerts_generated: int = 0
    errors: int = 0
    last_decision_time: Optional[datetime] = None
    last_optimization_time: Optional[datetime] = None
    subsystem_status: Dict[str, str] = field(default_factory=dict)


class SupplyChainEngine:
    """
    Core Supply Chain AI Engine.
    
    Orchestrates all supply chain intelligence subsystems:
    - Inventory AI
    - Demand AI
    - Procurement AI
    - Supplier AI
    - Logistics AI
    - Warehouse AI
    - Forecasting AI
    - Optimization AI
    """
    
    def __init__(self, config: EngineConfig):
        self.config = config
        self.metrics = EngineMetrics()
        self._subsystems: Dict[str, Any] = {}
        self._decision_handlers: Dict[str, Callable] = {}
        self._running = False
        self._main_task: Optional[asyncio.Task] = None
        self._decision_loop_task: Optional[asyncio.Task] = None
        
    async def initialize(self) -> None:
        """Initialize all subsystems and start the engine."""
        logger.info("Initializing Supply Chain AI Engine...")
        self.metrics.state = EngineState.INITIALIZING
        self.metrics.start_time = datetime.utcnow()
        
        await self._initialize_subsystems()
        await self._register_event_handlers()
        await self._warm_up_models()
        
        self.metrics.state = EngineState.RUNNING
        logger.info("Supply Chain AI Engine initialized successfully")
        
    async def start(self) -> None:
        """Start the engine's main decision loop."""
        if self._running:
            logger.warning("Engine already running")
            return
            
        self._running = True
        self._decision_loop_task = asyncio.create_task(self._decision_loop())
        logger.info("Supply Chain AI Engine started")
        
    async def stop(self) -> None:
        """Stop the engine gracefully."""
        logger.info("Stopping Supply Chain AI Engine...")
        self._running = False
        
        if self._decision_loop_task:
            self._decision_loop_task.cancel()
            try:
                await self._decision_loop_task
            except asyncio.CancelledError:
                pass
                
        await self._shutdown_subsystems()
        self.metrics.state = EngineState.STOPPED
        logger.info("Supply Chain AI Engine stopped")
        
    async def pause(self) -> None:
        """Pause the engine's decision loop."""
        self._running = False
        self.metrics.state = EngineState.PAUSED
        logger.info("Supply Chain AI Engine paused")
        
    async def resume(self) -> None:
        """Resume the engine's decision loop."""
        if not self._running:
            self._running = True
            self._decision_loop_task = asyncio.create_task(self._decision_loop())
            self.metrics.state = EngineState.RUNNING
            logger.info("Supply Chain AI Engine resumed")
            
    async def _initialize_subsystems(self) -> None:
        """Initialize all AI subsystems."""
        from .inventory.inventory_engine import InventoryEngine
        from .demand.demand_engine import DemandEngine
        from .procurement.procurement_engine import ProcurementEngine
        from .suppliers.supplier_engine import SupplierEngine
        from .logistics.logistics_engine import LogisticsEngine
        from .warehouse.warehouse_engine import WarehouseEngine
        from .forecasting.supply_forecaster import SupplyForecaster
        from .optimization.optimization_engine import OptimizationEngine
        
        self._subsystems = {
            "inventory": InventoryEngine(self.config.config, self.config.context, self.config.event_bus),
            "demand": DemandEngine(self.config.config, self.config.context, self.config.event_bus),
            "procurement": ProcurementEngine(self.config.config, self.config.context, self.config.event_bus),
            "suppliers": SupplierEngine(self.config.config, self.config.context, self.config.event_bus),
            "logistics": LogisticsEngine(self.config.config, self.config.context, self.config.event_bus),
            "warehouse": WarehouseEngine(self.config.config, self.config.context, self.config.event_bus),
            "forecasting": SupplyForecaster(self.config.config, self.config.context, self.config.event_bus),
            "optimization": OptimizationEngine(self.config.config, self.config.context, self.config.event_bus),
        }
        
        for name, subsystem in self._subsystems.items():
            await subsystem.initialize()
            self.metrics.subsystem_status[name] = "initialized"
            logger.info(f"Subsystem '{name}' initialized")
            
    async def _register_event_handlers(self) -> None:
        """Register event handlers for cross-subsystem communication."""
        self.config.event_bus.subscribe(EventType.INVENTORY_LOW, self._handle_inventory_low)
        self.config.event_bus.subscribe(EventType.DEMAND_SPIKE_DETECTED, self._handle_demand_spike)
        self.config.event_bus.subscribe(EventType.SUPPLIER_RISK_DETECTED, self._handle_supplier_risk)
        self.config.event_bus.subscribe(EventType.LOGISTICS_DELAY, self._handle_logistics_delay)
        self.config.event_bus.subscribe(EventType.WAREHOUSE_CAPACITY_WARNING, self._handle_warehouse_capacity)
        
    async def _warm_up_models(self) -> None:
        """Warm up ML models for faster inference."""
        logger.info("Warming up ML models...")
        await asyncio.gather(*[
            subsystem.warm_up() 
            for subsystem in self._subsystems.values() 
            if hasattr(subsystem, 'warm_up')
        ])
        logger.info("ML models warmed up")
        
    async def _decision_loop(self) -> None:
        """Main autonomous decision-making loop."""
        while self._running:
            try:
                await self._make_autonomous_decisions()
                await asyncio.sleep(self.config.decision_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in decision loop: {e}")
                self.metrics.errors += 1
                await asyncio.sleep(60)
                
    async def _make_autonomous_decisions(self) -> None:
        """Make autonomous supply chain decisions."""
        if not self.config.enable_autonomous_mode:
            return
            
        self.metrics.last_decision_time = datetime.utcnow()
        
        inventory_snapshot = await self._subsystems["inventory"].get_current_snapshot()
        demand_forecast = await self._subsystems["demand"].get_forecast(horizon_days=30)
        supplier_status = await self._subsystems["suppliers"].get_all_status()
        logistics_status = await self._subsystems["logistics"].get_status()
        
        optimization_result = await self._subsystems["optimization"].optimize(
            inventory=inventory_snapshot,
            demand_forecast=demand_forecast,
            supplier_status=supplier_status,
            logistics_status=logistics_status,
        )
        
        if optimization_result.replenishment_orders:
            for order in optimization_result.replenishment_orders:
                if order.estimated_cost <= self.config.auto_approval_threshold:
                    await self._execute_replenishment(order)
                    self.metrics.replenishments_triggered += 1
                else:
                    await self._request_approval(order)
                    
        if optimization_result.logistics_optimizations:
            await self._apply_logistics_optimizations(optimization_result.logistics_optimizations)
            
        if optimization_result.warehouse_optimizations:
            await self._apply_warehouse_optimizations(optimization_result.warehouse_optimizations)
            
        self.metrics.decisions_made += 1
        self.metrics.optimizations_run += 1
        self.metrics.last_optimization_time = datetime.utcnow()
        
    async def _execute_replenishment(self, order) -> None:
        """Execute an approved replenishment order."""
        await self._subsystems["procurement"].create_purchase_order(order)
        await self.config.event_bus.publish(SupplyChainEvent(
            event_type=EventType.REPLENISHMENT_EXECUTED,
            payload={"order_id": order.id, "items": order.items}
        ))
        
    async def _request_approval(self, order) -> None:
        """Request human approval for high-value orders."""
        await self.config.event_bus.publish(SupplyChainEvent(
            event_type=EventType.APPROVAL_REQUIRED,
            payload={"order_id": order.id, "estimated_cost": order.estimated_cost}
        ))
        
    async def _apply_logistics_optimizations(self, optimizations) -> None:
        """Apply logistics route optimizations."""
        await self._subsystems["logistics"].apply_optimizations(optimizations)
        
    async def _apply_warehouse_optimizations(self, optimizations) -> None:
        """Apply warehouse layout optimizations."""
        await self._subsystems["warehouse"].apply_optimizations(optimizations)
        
    async def _handle_inventory_low(self, event: SupplyChainEvent) -> None:
        """Handle low inventory alerts."""
        self.metrics.alerts_generated += 1
        await self._subsystems["inventory"].handle_low_stock(event.payload)
        
    async def _handle_demand_spike(self, event: SupplyChainEvent) -> None:
        """Handle demand spike detection."""
        self.metrics.alerts_generated += 1
        await self._subsystems["demand"].handle_spike(event.payload)
        await self._subsystems["procurement"].prepare_emergency_procurement(event.payload)
        
    async def _handle_supplier_risk(self, event: SupplyChainEvent) -> None:
        """Handle supplier risk detection."""
        self.metrics.alerts_generated += 1
        await self._subsystems["suppliers"].handle_risk(event.payload)
        await self._subsystems["procurement"].find_alternative_suppliers(event.payload)
        
    async def _handle_logistics_delay(self, event: SupplyChainEvent) -> None:
        """Handle logistics delay events."""
        self.metrics.alerts_generated += 1
        await self._subsystems["logistics"].handle_delay(event.payload)
        await self._subsystems["inventory"].adjust_for_delay(event.payload)
        
    async def _handle_warehouse_capacity(self, event: SupplyChainEvent) -> None:
        """Handle warehouse capacity warnings."""
        self.metrics.alerts_generated += 1
        await self._subsystems["warehouse"].handle_capacity_warning(event.payload)
        
    async def _shutdown_subsystems(self) -> None:
        """Gracefully shutdown all subsystems."""
        for name, subsystem in self._subsystems.items():
            try:
                await subsystem.shutdown()
                self.metrics.subsystem_status[name] = "stopped"
            except Exception as e:
                logger.error(f"Error shutting down {name}: {e}")
                self.metrics.subsystem_status[name] = "error"
                
    async def get_demand_forecast(self, horizon_days: int = 30) -> DemandForecast:
        """Get demand forecast for specified horizon."""
        self.metrics.predictions_made += 1
        return await self._subsystems["demand"].get_forecast(horizon_days)
        
    async def get_inventory_status(self) -> InventorySnapshot:
        """Get current inventory status."""
        return await self._subsystems["inventory"].get_current_snapshot()
        
    async def get_procurement_plan(self, horizon_days: int = 30) -> ProcurementPlan:
        """Get procurement plan for specified horizon."""
        return await self._subsystems["procurement"].get_plan(horizon_days)
        
    async def get_supplier_evaluations(self) -> List[SupplierEvaluation]:
        """Get all supplier evaluations."""
        return await self._subsystems["suppliers"].get_all_evaluations()
        
    async def get_logistics_plan(self) -> LogisticsPlan:
        """Get current logistics plan."""
        return await self._subsystems["logistics"].get_plan()
        
    async def get_warehouse_layout(self) -> WarehouseLayout:
        """Get current warehouse layout."""
        return await self._subsystems["warehouse"].get_layout()
        
    async def run_optimization(self, scenario: Optional[Dict] = None) -> OptimizationResult:
        """Run global supply chain optimization."""
        self.metrics.optimizations_run += 1
        return await self._subsystems["optimization"].optimize(scenario)
        
    async def simulate_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run digital twin simulation for a scenario."""
        return await self._subsystems["optimization"].simulate(scenario)
        
    async def get_kpis(self) -> Dict[str, float]:
        """Get current supply chain KPIs."""
        from .supply_metrics import KPICalculator
        calculator = KPICalculator(self.config.context)
        return await calculator.calculate_all()
        
    def get_metrics(self) -> EngineMetrics:
        """Get engine runtime metrics."""
        return self.metrics
        
    def get_subsystem(self, name: str):
        """Get a specific subsystem by name."""
        return self._subsystems.get(name)