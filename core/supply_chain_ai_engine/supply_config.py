"""
Supply Chain Configuration - Global configuration for the supply chain AI engine.

Central configuration management for all supply chain subsystems.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


@dataclass
class InventoryConfig:
    enable_monitoring: bool = True
    low_stock_threshold_days: int = 7
    critical_stock_threshold_days: int = 2
    auto_reorder_enabled: bool = True
    auto_approve_reorder: bool = False
    max_safety_stock_multiplier: float = 2.0
    min_safety_stock_multiplier: float = 0.5
    default_reorder_point_days: int = 14
    stock_accuracy_warning_threshold: float = 97.0
    cycle_count_frequency_days: int = 30
    enable_excess_detection: bool = True
    excess_threshold_days: int = 90
    enable_waste_tracking: bool = True


@dataclass
class DemandConfig:
    enable_forecasting: bool = True
    forecast_horizon_days: int = 90
    forecast_interval_days: int = 1
    min_history_days: int = 365
    seasonality_detection_enabled: bool = True
    market_analysis_enabled: bool = True
    trend_detection_enabled: bool = True
    confidence_interval: float = 0.95
    spike_detection_sensitivity: float = 2.0
    drop_detection_sensitivity: float = 0.5
    external_data_enabled: bool = True
    holiday_calendar_enabled: bool = True
    weather_integration_enabled: bool = False


@dataclass
class ProcurementConfig:
    enable_auto_procurement: bool = True
    emergency_order_surcharge: float = 1.2
    max_emergency_order_value: float = 50000.0
    require_approval_above: float = 100000.0
    preferred_supplier_premium: float = 0.05
    negotiation_target_savings: float = 0.1
    split_order_threshold: int = 1000
    enable_price_tracking: bool = True
    default_payment_terms: str = "net_30"
    order_consolidation_enabled: bool = True
    consolidation_window_hours: int = 48


@dataclass
class SupplierConfig:
    enable_scoring: bool = True
    score_weight_price: float = 0.2
    score_weight_quality: float = 0.3
    score_weight_delivery: float = 0.25
    score_weight_reliability: float = 0.15
    score_weight_risk: float = 0.1
    risk_warning_threshold: float = 0.6
    risk_critical_threshold: float = 0.8
    performance_review_interval_days: int = 30
    enable_automatic_requalification: bool = True
    new_supplier_probation_period_days: int = 90
    enable_contract_expiry_alerts: bool = True
    contract_expiry_warning_days: int = 60
    enable_alternative_search: bool = True


@dataclass
class LogisticsConfig:
    enable_route_optimization: bool = True
    enable_delivery_prediction: bool = True
    enable_cost_optimization: bool = True
    max_route_optimization_time: int = 60
    traffic_integration_enabled: bool = False
    fuel_cost_per_km: float = 0.4
    driver_cost_per_hour: float = 25.0
    vehicle_capacity_kg: float = 1000.0
    vehicle_capacity_m3: float = 20.0
    max_delivery_distance_km: float = 500.0
    enable_carbon_tracking: bool = True
    carbon_cost_per_kg: float = 0.05
    preferred_carriers: List[str] = field(default_factory=list)


@dataclass
class WarehouseConfig:
    enable_layout_optimization: bool = True
    enable_picking_optimization: bool = True
    enable_robotics_integration: bool = False
    capacity_warning_threshold: float = 0.85
    capacity_critical_threshold: float = 0.95
    optimize_frequency_days: int = 7
    max_relocation_per_day: int = 50
    picking_strategy: str = "zone"
    batch_picking_enabled: bool = True
    max_batch_size: int = 20
    enable_automated_putaway: bool = True
    location_recommendation_enabled: bool = True


@dataclass
class ForecastingConfig:
    enable_risk_prediction: bool = True
    enable_capacity_planning: bool = True
    risk_horizon_days: int = 60
    capacity_horizon_days: int = 180
    risk_probability_threshold: float = 0.6
    scenario_simulation_enabled: bool = True
    max_scenarios_per_run: int = 10
    enable_monte_carlo: bool = True
    monte_carlo_iterations: int = 1000
    confidence_level: float = 0.95


@dataclass
class OptimizationConfig:
    enable_global_optimization: bool = True
    enable_cost_optimization: bool = True
    enable_efficiency_analysis: bool = True
    enable_what_if_analysis: bool = True
    optimize_interval_hours: int = 6
    max_optimization_time_seconds: int = 300
    cost_saving_target: float = 0.05
    efficiency_target: float = 0.1
    risk_reduction_target: float = 0.2
    enable_digital_twin: bool = True
    digital_twin_update_interval_hours: int = 24


@dataclass
class SecurityConfig:
    enable_access_control: bool = True
    enable_encryption: bool = True
    enable_audit_logging: bool = True
    audit_retention_days: int = 365
    max_login_attempts: int = 5
    session_timeout_minutes: int = 60
    require_mfa: bool = False
    sensitive_fields: List[str] = field(default_factory=lambda: ["price", "cost", "discount", "contract_value"])
    enable_webhook_verification: bool = True


@dataclass
class IntegrationConfig:
    enable_erp_sync: bool = True
    erp_sync_interval_minutes: int = 60
    enable_financial_sync: bool = True
    financial_sync_interval_minutes: int = 1440
    enable_customer_ai_sync: bool = True
    customer_ai_sync_interval_minutes: int = 1440
    enable_robotics_sync: bool = False
    robotics_sync_interval_minutes: int = 60
    decision_center_enabled: bool = True
    decision_center_sync_interval_minutes: int = 1440
    api_rate_limit_per_minute: int = 60
    webhook_retry_max: int = 3
    webhook_retry_delay_seconds: int = 30


@dataclass
class SupplyChainConfig:
    """Master configuration for the entire Supply Chain AI Engine."""
    
    # General settings
    engine_name: str = "SupplyChainAIEngine"
    engine_version: str = "1.0.0"
    environment: str = "production"
    log_level: str = "INFO"
    enable_telemetry: bool = True
    config_path: str = ""
    
    # Subsystem configurations
    inventory: InventoryConfig = field(default_factory=InventoryConfig)
    demand: DemandConfig = field(default_factory=DemandConfig)
    procurement: ProcurementConfig = field(default_factory=ProcurementConfig)
    suppliers: SupplierConfig = field(default_factory=SupplierConfig)
    logistics: LogisticsConfig = field(default_factory=LogisticsConfig)
    warehouse: WarehouseConfig = field(default_factory=WarehouseConfig)
    forecasting: ForecastingConfig = field(default_factory=ForecastingConfig)
    optimization: OptimizationConfig = field(default_factory=OptimizationConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    integrations: IntegrationConfig = field(default_factory=IntegrationConfig)
    
    # Feature flags
    enable_digital_twin: bool = True
    enable_autonomous_replenishment: bool = True
    enable_self_healing: bool = False
    enable_continuous_learning: bool = True
    
    # Resource limits
    max_concurrent_operations: int = 10
    max_queue_size: int = 1000
    operation_timeout_seconds: int = 30
    
    _extra: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SupplyChainConfig":
        """Create config from dictionary."""
        config = cls()
        for key, value in data.items():
            if hasattr(config, key) and not key.startswith("_"):
                if isinstance(value, dict) and key in cls.__dataclass_fields__:
                    subconfig = getattr(config, key)
                    if hasattr(subconfig, "__dataclass_fields__"):
                        for sub_key, sub_value in value.items():
                            if hasattr(subconfig, sub_key):
                                setattr(subconfig, sub_key, sub_value)
                        continue
                setattr(config, key, value)
            else:
                config._extra[key] = value
        return config
    
    @classmethod
    def from_json(cls, json_path: str) -> "SupplyChainConfig":
        """Load config from JSON file."""
        if not os.path.exists(json_path):
            logger.warning(f"Config file not found: {json_path}, using defaults")
            return cls()
        with open(json_path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)
    
    def to_json(self, json_path: str) -> None:
        """Save config to JSON file."""
        with open(json_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)
        logger.info(f"Config saved to {json_path}")
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of warnings/errors."""
        errors = []
        if self.inventory.low_stock_threshold_days <= 0:
            errors.append("low_stock_threshold_days must be positive")
        if self.inventory.critical_stock_threshold_days <= 0:
            errors.append("critical_stock_threshold_days must be positive")
        if self.demand.forecast_horizon_days < 1:
            errors.append("forecast_horizon_days must be at least 1")
        if self.optimization.optimize_interval_hours < 1:
            errors.append("optimize_interval_hours must be at least 1")
        return errors