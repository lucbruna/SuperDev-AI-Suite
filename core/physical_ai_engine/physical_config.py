from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class RoboticsConfig:
    enable_autonomous_navigation: bool = True
    enable_collision_avoidance: bool = True
    max_robot_speed: float = 2.0
    default_battery_threshold: float = 20.0
    task_retry_limit: int = 3
    enable_robot_learning: bool = True


@dataclass
class AutomationConfig:
    enable_process_control: bool = True
    enable_machine_monitoring: bool = True
    plc_poll_interval_ms: int = 100
    max_machines_per_controller: int = 50
    safety_timeout_seconds: int = 5


@dataclass
class IoTConfig:
    enable_device_registry: bool = True
    enable_telemetry: bool = True
    mqtt_broker: str = "localhost"
    mqtt_port: int = 1883
    telemetry_buffer_size: int = 10000
    device_timeout_seconds: int = 30


@dataclass
class SensorsConfig:
    enable_anomaly_detection: bool = True
    enable_sensor_fusion: bool = True
    sampling_rate_default: float = 10.0
    calibration_interval_days: int = 90
    anomaly_threshold: float = 3.0


@dataclass
class VisionConfig:
    enable_object_detection: bool = True
    enable_quality_inspection: bool = True
    enable_defect_detection: bool = True
    camera_resolution: str = "1920x1080"
    processing_fps: int = 30
    confidence_threshold: float = 0.7


@dataclass
class MotionConfig:
    enable_path_planning: bool = True
    enable_collision_detection: bool = True
    path_optimization: str = "shortest"
    safety_distance_m: float = 0.5
    max_acceleration: float = 1.0


@dataclass
class SimulationConfig:
    enable_physics_engine: bool = True
    enable_scenario_testing: bool = True
    max_simulation_steps: int = 100000
    simulation_timestep: float = 0.01
    enable_rendering: bool = False


@dataclass
class DigitalTwinConfig:
    enable_virtual_replica: bool = True
    enable_state_sync: bool = True
    enable_prediction: bool = True
    sync_interval_ms: int = 1000
    history_retention_days: int = 365


@dataclass
class MaintenanceConfig:
    enable_predictive_maintenance: bool = True
    enable_failure_prediction: bool = True
    maintenance_lead_time_days: int = 7
    criticality_threshold: float = 0.8
    schedule_optimization: bool = True


@dataclass
class SecurityConfig:
    enable_device_auth: bool = True
    enable_access_control: bool = True
    enable_safety_monitor: bool = True
    enable_emergency_stop: bool = True
    max_auth_attempts: int = 3
    safety_zone_m: float = 1.0


@dataclass
class PhysicalConfig:
    engine_name: str = "PhysicalAIEngine"
    engine_version: str = "1.0.0"
    environment: str = "production"
    log_level: str = "INFO"
    enable_telemetry: bool = True
    enable_autonomous_operations: bool = False
    enable_safety_override: bool = False
    max_concurrent_tasks: int = 10
    robotics: RoboticsConfig = field(default_factory=RoboticsConfig)
    automation: AutomationConfig = field(default_factory=AutomationConfig)
    iot: IoTConfig = field(default_factory=IoTConfig)
    sensors: SensorsConfig = field(default_factory=SensorsConfig)
    vision: VisionConfig = field(default_factory=VisionConfig)
    motion: MotionConfig = field(default_factory=MotionConfig)
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    digital_twin: DigitalTwinConfig = field(default_factory=DigitalTwinConfig)
    maintenance: MaintenanceConfig = field(default_factory=MaintenanceConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    _extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PhysicalConfig:
        config = cls()
        for key, value in data.items():
            if hasattr(config, key) and not key.startswith("_"):
                if isinstance(value, dict) and key in cls.__dataclass_fields__:
                    sub = getattr(config, key)
                    if hasattr(sub, "__dataclass_fields__"):
                        for sk, sv in value.items():
                            if hasattr(sub, sk):
                                setattr(sub, sk, sv)
                        continue
                setattr(config, key, value)
            else:
                config._extra[key] = value
        return config

    @classmethod
    def from_json(cls, path: str) -> PhysicalConfig:
        if not os.path.exists(path):
            return cls()
        with open(path) as f:
            return cls.from_dict(json.load(f))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

    def validate(self) -> List[str]:
        errors = []
        if self.vision.confidence_threshold < 0 or self.vision.confidence_threshold > 1:
            errors.append("confidence_threshold must be between 0 and 1")
        if self.maintenance.criticality_threshold < 0 or self.maintenance.criticality_threshold > 1:
            errors.append("criticality_threshold must be between 0 and 1")
        return errors
