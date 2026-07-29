from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class RobotType(Enum):
    INDUSTRIAL_ARM = "industrial_arm"
    MOBILE = "mobile"
    COLLABORATIVE = "collaborative"
    HUMANOID = "humanoid"
    DRONE = "drone"
    AGV = "agv"
    CUSTOM = "custom"


class RobotStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    CHARGING = "charging"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    EMERGENCY_STOP = "emergency_stop"
    OFFLINE = "offline"


class DeviceType(Enum):
    PLC = "plc"
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    MOTOR = "motor"
    CONVEYOR = "conveyor"
    PUMP = "pump"
    VALVE = "valve"
    ROBOT = "robot"
    CAMERA = "camera"
    DRONE = "drone"
    GENERIC = "generic"


class DeviceProtocol(Enum):
    MODBUS = "modbus"
    OPC_UA = "opc_ua"
    MQTT = "mqtt"
    PROFINET = "profinet"
    ETHERNET_IP = "ethernet_ip"
    CAN = "can"
    BACNET = "bacnet"
    CUSTOM = "custom"


class SensorType(Enum):
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    VIBRATION = "vibration"
    HUMIDITY = "humidity"
    PROXIMITY = "proximity"
    LIGHT = "light"
    SOUND = "sound"
    FORCE = "force"
    TORQUE = "torque"
    FLOW = "flow"
    LEVEL = "level"
    GAS = "gas"
    SPEED = "speed"
    POSITION = "position"
    ACCELERATION = "acceleration"
    CURRENT = "current"
    VOLTAGE = "voltage"
    POWER = "power"


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MaintenanceType(Enum):
    PREVENTIVE = "preventive"
    PREDICTIVE = "predictive"
    CORRECTIVE = "corrective"
    CONDITION_BASED = "condition_based"


class SimulationStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Robot:
    id: str
    name: str
    robot_type: RobotType = RobotType.INDUSTRIAL_ARM
    status: RobotStatus = RobotStatus.IDLE
    position: Dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    orientation: Dict[str, float] = field(default_factory=lambda: {"roll": 0, "pitch": 0, "yaw": 0})
    battery_level: float = 100.0
    speed: float = 0.0
    payload_kg: float = 0.0
    firmware_version: str = "1.0.0"
    connected: bool = False
    last_heartbeat: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RobotTask:
    id: str
    robot_id: str
    task_type: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    progress: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_duration_seconds: int = 0
    priority: int = 0


@dataclass
class Device:
    id: str
    name: str
    device_type: DeviceType = DeviceType.GENERIC
    protocol: DeviceProtocol = DeviceProtocol.MQTT
    ip_address: str = ""
    port: int = 0
    location: str = ""
    status: str = "unknown"
    last_seen: Optional[datetime] = None
    config: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class SensorReading:
    id: str
    sensor_id: str
    sensor_type: SensorType = SensorType.TEMPERATURE
    value: float = 0.0
    unit: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    quality: float = 1.0
    location: str = ""


@dataclass
class SensorConfig:
    id: str
    name: str
    sensor_type: SensorType = SensorType.TEMPERATURE
    min_range: float = 0.0
    max_range: float = 100.0
    unit: str = ""
    sampling_rate_hz: float = 1.0
    calibration_date: Optional[datetime] = None
    calibration_due: Optional[datetime] = None
    location: str = ""
    alerts_enabled: bool = True
    min_threshold: float = 0.0
    max_threshold: float = 100.0


@dataclass
class TelemetryData:
    device_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metrics: Dict[str, float] = field(default_factory=dict)
    status: str = "normal"
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MachineState:
    machine_id: str
    state: str = "stopped"
    speed: float = 0.0
    temperature: float = 0.0
    pressure: float = 0.0
    power_consumption: float = 0.0
    cycle_count: int = 0
    uptime_hours: float = 0.0
    last_maintenance: Optional[datetime] = None
    alerts: List[str] = field(default_factory=list)


@dataclass
class ProductionOrder:
    id: str
    product: str
    quantity: int = 0
    produced: int = 0
    defective: int = 0
    status: str = "planned"
    start_time: Optional[datetime] = None
    estimated_end: Optional[datetime] = None
    line: str = ""


@dataclass
class VisionInspection:
    id: str
    camera_id: str
    product_id: str = ""
    passed: bool = True
    defects: List[str] = field(default_factory=list)
    confidence: float = 0.0
    processing_time_ms: float = 0.0
    image_reference: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MotionPlan:
    id: str
    robot_id: str
    waypoints: List[Dict[str, float]] = field(default_factory=list)
    total_distance: float = 0.0
    estimated_time_seconds: float = 0.0
    energy_estimate: float = 0.0
    collision_risks: List[str] = field(default_factory=list)
    status: str = "planned"


@dataclass
class CollisionRisk:
    id: str
    robot_id: str
    obstacle_id: str
    distance: float = 0.0
    probability: float = 0.0
    severity: str = "low"
    recommended_action: str = ""


@dataclass
class SimulationResult:
    id: str
    scenario_name: str
    duration_seconds: float = 0.0
    cycles_completed: int = 0
    passed: bool = True
    issues: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DigitalTwin:
    id: str
    asset_id: str
    asset_type: str = ""
    name: str = ""
    state: Dict[str, Any] = field(default_factory=dict)
    last_sync: Optional[datetime] = None
    health_score: float = 100.0
    prediction: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MaintenanceRecord:
    id: str
    asset_id: str
    maintenance_type: MaintenanceType = MaintenanceType.PREVENTIVE
    description: str = ""
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    cost: float = 0.0
    technician: str = ""
    parts_used: List[str] = field(default_factory=list)
    status: str = "scheduled"


@dataclass
class FailurePrediction:
    id: str
    asset_id: str
    failure_mode: str = ""
    probability: float = 0.0
    estimated_time_to_failure_hours: float = 0.0
    confidence: float = 0.0
    recommended_actions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PhysicalAlert:
    id: str
    source: str
    alert_type: str
    message: str
    level: AlertLevel = AlertLevel.INFO
    asset_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class EnvironmentData:
    temperature: float = 25.0
    humidity: float = 60.0
    pressure: float = 1013.25
    lighting_lux: float = 500.0
    noise_db: float = 40.0
    air_quality: str = "good"
    vibration: float = 0.0
