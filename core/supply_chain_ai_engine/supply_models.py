"""
Supply Chain Models - Data models for the supply chain engine.

Core domain models used throughout the supply chain AI system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class StockStatus(Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    CRITICAL = "critical"
    OUT_OF_STOCK = "out_of_stock"
    EXCESS = "excess"
    DISCONTINUED = "discontinued"


class OrderStatus(Enum):
    DRAFT = "draft"
    PLANNED = "planned"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    PLACED = "placed"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    RECEIVED = "received"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    PARTIALLY_RECEIVED = "partially_received"


class SupplierStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_REVIEW = "pending_review"
    SUSPENDED = "suspended"
    BLACKLISTED = "blacklisted"


class SupplierRiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LogisticsMode(Enum):
    ROAD = "road"
    AIR = "air"
    SEA = "sea"
    RAIL = "rail"
    MULTIMODAL = "multimodal"


class WarehouseZone(Enum):
    RECEIVING = "receiving"
    STORAGE = "storage"
    PICKING = "picking"
    PACKING = "packing"
    SHIPPING = "shipping"
    RETURN = "return"
    CROSS_DOCK = "cross_dock"


@dataclass
class Product:
    id: str
    sku: str
    name: str
    category: str
    unit: str
    weight_kg: float = 0.0
    volume_m3: float = 0.0
    price: float = 0.0
    cost: float = 0.0
    is_perishable: bool = False
    shelf_life_days: Optional[int] = None
    min_stock_level: int = 0
    max_stock_level: int = 10000
    reorder_point: int = 100
    lead_time_days: int = 7
    preferred_suppliers: List[str] = field(default_factory=list)


@dataclass
class InventoryItem:
    product_id: str
    sku: str
    product_name: str
    current_stock: int
    reserved_stock: int = 0
    available_stock: int = 0
    incoming_stock: int = 0
    status: StockStatus = StockStatus.IN_STOCK
    location: str = ""
    last_counted: Optional[datetime] = None
    reorder_point: int = 0
    optimal_level: int = 0
    
    @property
    def available(self) -> int:
        return self.current_stock - self.reserved_stock
        
    @property
    def is_low(self) -> bool:
        return self.available <= self.reorder_point
        
    @property
    def days_remaining(self) -> float:
        return 0.0


@dataclass
class InventorySnapshot:
    timestamp: datetime = field(default_factory=datetime.utcnow)
    items: Dict[str, InventoryItem] = field(default_factory=dict)
    total_items: int = 0
    total_value: float = 0.0
    low_stock_count: int = 0
    out_of_stock_count: int = 0
    excess_count: int = 0
    
    def get_product_quantity(self, product_id: str) -> int:
        item = self.items.get(product_id)
        return item.current_stock if item else 0
        
    def get_available_quantity(self, product_id: str) -> int:
        item = self.items.get(product_id)
        return item.available if item else 0


@dataclass
class DemandForecast:
    product_id: str
    forecast_date: datetime
    horizon_days: int
    predictions: Dict[str, float] = field(default_factory=dict)
    confidence_intervals: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    seasonality_factors: Dict[str, float] = field(default_factory=dict)
    trend_direction: float = 0.0
    volatility: float = 0.0
    
    def get_daily_forecast(self, date: str) -> float:
        return self.predictions.get(date, 0.0)
        
    def get_total_forecast(self) -> float:
        return sum(self.predictions.values())
        
    def get_product_forecast(self, product_id: str) -> Dict[str, Any]:
        return {
            "predictions": self.predictions,
            "confidence_intervals": self.confidence_intervals,
            "total": self.get_total_forecast(),
        }


@dataclass
class ProcurementOrder:
    id: str
    supplier_id: str
    items: Dict[str, int]
    estimated_cost: float = 0.0
    actual_cost: float = 0.0
    status: OrderStatus = OrderStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None
    placed_at: Optional[datetime] = None
    expected_delivery: Optional[datetime] = None
    received_at: Optional[datetime] = None
    notes: str = ""
    created_by: str = "system"
    approved_by: Optional[str] = None
    is_emergency: bool = False
    priority: int = 0


@dataclass
class ProcurementPlan:
    horizon_days: int
    orders: List[ProcurementOrder] = field(default_factory=list)
    total_cost: float = 0.0
    total_savings: float = 0.0
    risk_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)


@dataclass
class Supplier:
    id: str
    name: str
    contact_email: str
    contact_phone: str = ""
    address: str = ""
    status: SupplierStatus = SupplierStatus.ACTIVE
    categories: List[str] = field(default_factory=list)
    products: List[str] = field(default_factory=list)
    rating: float = 5.0
    total_orders: int = 0
    on_time_rate: float = 100.0
    quality_rate: float = 100.0
    average_lead_time_days: int = 7
    payment_terms: str = "net_30"
    contract_end: Optional[datetime] = None
    risk_level: SupplierRiskLevel = SupplierRiskLevel.LOW
    notes: str = ""


@dataclass
class SupplierEvaluation:
    supplier_id: str
    supplier_name: str
    overall_score: float
    price_score: float = 0.0
    quality_score: float = 0.0
    delivery_score: float = 0.0
    reliability_score: float = 0.0
    risk_score: float = 0.0
    evaluated_at: datetime = field(default_factory=datetime.utcnow)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class LogisticsRoute:
    id: str
    origin: str
    destination: str
    mode: LogisticsMode = LogisticsMode.ROAD
    distance_km: float = 0.0
    estimated_time_hours: float = 0.0
    cost: float = 0.0
    fuel_cost: float = 0.0
    toll_cost: float = 0.0
    carbon_emissions_kg: float = 0.0
    priority: int = 0
    is_optimized: bool = False


@dataclass
class LogisticsPlan:
    routes: List[LogisticsRoute] = field(default_factory=list)
    total_cost: float = 0.0
    total_distance: float = 0.0
    total_emissions: float = 0.0
    average_delivery_time: float = 0.0
    on_time_rate: float = 0.0
    optimization_rate: float = 0.0


@dataclass
class WarehouseLocation:
    id: str
    zone: WarehouseZone
    aisle: str
    rack: str
    level: int
    is_primary: bool = False
    capacity: int = 100
    current_occupancy: int = 0
    products: List[str] = field(default_factory=list)
    access_frequency: int = 0
    picking_priority: int = 0


@dataclass
class WarehouseLayout:
    locations: Dict[str, WarehouseLocation] = field(default_factory=dict)
    total_capacity: int = 0
    current_utilization: float = 0.0
    total_products: int = 0
    last_optimized: Optional[datetime] = None
    picking_efficiency: float = 0.0
    relocation_recommendations: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ReplenishmentOrder:
    id: str
    product_id: str
    quantity: int
    estimated_cost: float = 0.0
    priority: int = 0
    suggested_supplier_id: Optional[str] = None
    reason: str = ""
    is_automatic: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class OptimizationResult:
    timestamp: datetime = field(default_factory=datetime.utcnow)
    cost_savings: float = 0.0
    efficiency_gain: float = 0.0
    risk_reduction: float = 0.0
    replenishment_orders: List[ReplenishmentOrder] = field(default_factory=list)
    logistics_optimizations: List[LogisticsRoute] = field(default_factory=list)
    warehouse_optimizations: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    scenarios_simulated: int = 0


@dataclass
class RiskPrediction:
    risk_id: str
    risk_type: str
    probability: float
    impact: float
    risk_score: float
    description: str
    affected_products: List[str] = field(default_factory=list)
    affected_suppliers: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)
    predicted_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CapacityPlan:
    period_start: datetime
    period_end: datetime
    current_capacity: float
    required_capacity: float
    capacity_gap: float
    expansion_recommended: bool = False
    expansion_cost: float = 0.0
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ScenarioSimulation:
    scenario_id: str
    scenario_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    execution_time_ms: float = 0.0


@dataclass
class SupplyChainAlert:
    id: str
    alert_type: str
    severity: str
    title: str
    message: str
    affected_items: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    recommended_action: str = ""