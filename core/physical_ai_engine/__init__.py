"""
Autonomous Robotics & Physical World AI Engine

Enterprise physical intelligence platform providing:
- Intelligent robot control & fleet management
- Industrial automation & machine integration
- IoT device management & telemetry
- Sensor intelligence & anomaly detection
- Computer vision & quality inspection
- Motion control & collision avoidance
- Physics simulation & scenario testing
- Digital twin & virtual replicas
- Predictive maintenance & failure prediction
"""

from .physical_engine import PhysicalEngine, EngineConfig, EngineState, EngineMetrics
from .robotics_manager import RoboticsManager, ManagerConfig
from .device_manager import DeviceManager
from .physical_context import PhysicalContext
from .physical_events import PhysicalEventBus, PhysicalEvent, EventType
from .physical_metrics import PhysicalMetrics, MetricsCollector
from .physical_interfaces import (
    RobotInterface, DeviceInterface, SensorInterface, SimulationInterface,
    ConcreteRobotInterface, ConcreteDeviceInterface, ConcreteSensorInterface, ConcreteSimulationInterface,
)
from .physical_models import *
from .physical_config import PhysicalConfig
from .physical_security import PhysicalSecurityManager

from .robotics import RoboticsEngine, RobotController, TaskPlanner, RobotNavigation, RobotLearning
from .automation import AutomationEngine, ProcessController, MachineInterface, PLCConnector, IndustrialProtocols
from .iot import IoTEngine, DeviceRegistry, Communication, TelemetryManager, ProtocolAdapter
from .sensors import SensorEngine, DataReader, Calibration, AnomalyDetection, SensorFusion
from .vision_control import VisionEngine, CameraManager, ObjectTracking, QualityInspection, DefectDetection
from .motion import MotionEngine, PathPlanning, MovementControl, CollisionDetection
from .simulation import SimulationEngine, EnvironmentModel, PhysicsSimulator, ScenarioTesting
from .digital_twin import TwinEngine, VirtualReplica, StateSync, TwinPrediction
from .maintenance import MaintenanceEngine, PredictiveModel, FailurePrediction, MaintenanceScheduler

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

__all__ = [
    "PhysicalEngine", "EngineConfig", "EngineState", "EngineMetrics",
    "RoboticsManager", "ManagerConfig", "DeviceManager",
    "PhysicalContext", "PhysicalEventBus", "PhysicalEvent", "EventType",
    "PhysicalMetrics", "MetricsCollector",
    "RobotInterface", "DeviceInterface", "SensorInterface", "SimulationInterface",
    "ConcreteRobotInterface", "ConcreteDeviceInterface", "ConcreteSensorInterface", "ConcreteSimulationInterface",
    "PhysicalSecurityManager", "PhysicalConfig",
    "RoboticsEngine", "RobotController", "TaskPlanner", "RobotNavigation", "RobotLearning",
    "AutomationEngine", "ProcessController", "MachineInterface", "PLCConnector", "IndustrialProtocols",
    "IoTEngine", "DeviceRegistry", "Communication", "TelemetryManager", "ProtocolAdapter",
    "SensorEngine", "DataReader", "Calibration", "AnomalyDetection", "SensorFusion",
    "VisionEngine", "CameraManager", "ObjectTracking", "QualityInspection", "DefectDetection",
    "MotionEngine", "PathPlanning", "MovementControl", "CollisionDetection",
    "SimulationEngine", "EnvironmentModel", "PhysicsSimulator", "ScenarioTesting",
    "TwinEngine", "VirtualReplica", "StateSync", "TwinPrediction",
    "MaintenanceEngine", "PredictiveModel", "FailurePrediction", "MaintenanceScheduler",
]
