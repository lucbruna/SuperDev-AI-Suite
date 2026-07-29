"""
Tests for the Physical AI Engine core components.
"""

import pytest
from datetime import datetime
from ..physical_engine import PhysicalEngine, EngineConfig, EngineState, EngineMetrics
from ..robotics_manager import RoboticsManager, ManagerConfig
from ..device_manager import DeviceManager
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus, PhysicalEvent, EventType
from ..physical_models import (
    Robot, RobotStatus, RobotType, Device, DeviceType, DeviceProtocol,
    SensorReading, SensorType, VisionInspection, MaintenanceRecord,
    MaintenanceType, FailurePrediction, MotionPlan, SimulationResult,
    DigitalTwin, PhysicalAlert, AlertLevel, MachineState, ProductionOrder,
    TelemetryData,
)
from ..physical_config import PhysicalConfig
from ..physical_security import PhysicalSecurityManager
from ..physical_interfaces import ConcreteRobotInterface, ConcreteDeviceInterface


class TestPhysicalEngine:
    @pytest.mark.asyncio
    async def test_initialize(self):
        config = PhysicalConfig()
        event_bus = PhysicalEventBus()
        context = PhysicalContext()
        security = PhysicalSecurityManager(config)
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context, security=security)
        engine = PhysicalEngine(engine_config)
        await engine.initialize()
        assert engine.metrics.state == EngineState.RUNNING

    @pytest.mark.asyncio
    async def test_stop(self):
        config = PhysicalConfig()
        event_bus = PhysicalEventBus()
        context = PhysicalContext()
        security = PhysicalSecurityManager(config)
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context, security=security)
        engine = PhysicalEngine(engine_config)
        await engine.initialize()
        await engine.stop()
        assert engine.metrics.state == EngineState.STOPPED


class TestRoboticsManager:
    @pytest.mark.asyncio
    async def test_get_robots(self):
        config = PhysicalConfig()
        event_bus = PhysicalEventBus()
        context = PhysicalContext()
        security = PhysicalSecurityManager(config)
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context, security=security)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = RoboticsManager(manager_config)
        await manager.initialize()
        robots = await manager.get_robots()
        assert len(robots) > 0
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_assign_task(self):
        config = PhysicalConfig()
        event_bus = PhysicalEventBus()
        context = PhysicalContext()
        security = PhysicalSecurityManager(config)
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context, security=security)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = RoboticsManager(manager_config)
        await manager.initialize()
        task = await manager.assign_task("R-001", "pick_and_place", "Pick item from conveyor")
        assert task.robot_id == "R-001"
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_get_physical_kpis(self):
        config = PhysicalConfig()
        event_bus = PhysicalEventBus()
        context = PhysicalContext()
        security = PhysicalSecurityManager(config)
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context, security=security)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = RoboticsManager(manager_config)
        await manager.initialize()
        kpis = await manager.get_physical_kpis()
        assert "robots_active" in kpis
        await manager.shutdown()


class TestPhysicalEventBus:
    @pytest.mark.asyncio
    async def test_publish_subscribe(self):
        bus = PhysicalEventBus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe(EventType.DEVICE_CONNECTED, handler)
        event = PhysicalEvent(event_type=EventType.DEVICE_CONNECTED, payload={"device_id": "D-001"})
        await bus.publish_nowait(event)
        assert len(received) == 1
        assert received[0].event_type == EventType.DEVICE_CONNECTED

    def test_event_counts(self):
        bus = PhysicalEventBus()
        assert bus.get_event_count(EventType.ROBOT_STATUS_CHANGED) == 0


class TestPhysicalSecurity:
    def test_access_control(self):
        security = PhysicalSecurityManager()
        security.set_user_role("plant_mgr", "plant_manager")
        assert security.check_access("plant_mgr", "robot", "emergency_stop") is True
        assert security.check_access("plant_mgr", "robot", "override") is True

    def test_emergency_stop(self):
        security = PhysicalSecurityManager()
        entry = security.trigger_emergency_stop("operator1", "Collision risk detected")
        assert entry["id"] is not None
        assert security.is_emergency_active() is True
        security.reset_emergency_stop()
        assert security.is_emergency_active() is False

    def test_device_auth(self):
        security = PhysicalSecurityManager()
        security.register_device_credentials("D-001", "secret123")
        assert security.authenticate_device("D-001", "secret123") is True
        assert security.authenticate_device("D-001", "wrong") is False


class TestPhysicalModels:
    def test_robot(self):
        robot = Robot(id="R-001", name="Robô 1", robot_type=RobotType.COLLABORATIVE)
        assert robot.status == RobotStatus.IDLE
        assert robot.battery_level == 100.0

    def test_device(self):
        device = Device(id="D-001", name="Sensor 1", device_type=DeviceType.SENSOR, protocol=DeviceProtocol.MQTT)
        assert device.status == "unknown"

    def test_sensor_reading(self):
        sr = SensorReading(id="SR-001", sensor_id="S-TEMP-001", sensor_type=SensorType.TEMPERATURE, value=75.5)
        assert sr.value == 75.5

    def test_maintenance_record(self):
        mr = MaintenanceRecord(id="M-001", asset_id="MC-001", maintenance_type=MaintenanceType.PREDICTIVE)
        assert mr.status == "scheduled"

    def test_alert(self):
        alert = PhysicalAlert(id="A-001", source="sensor", alert_type="high_temp", message="Temp above 80C",
                              level=AlertLevel.CRITICAL)
        assert alert.level == AlertLevel.CRITICAL


class TestDeviceManager:
    def test_register_and_list(self):
        dm = DeviceManager()
        device = dm.register("Motor Principal", DeviceType.MOTOR, DeviceProtocol.MODBUS)
        assert device.name == "Motor Principal"
        assert len(dm.get_all()) == 1

    def test_telemetry(self):
        dm = DeviceManager()
        device = dm.register("Sensor Teste")
        data = dm.record_telemetry(device.id, {"temperature": 65.0, "pressure": 150.0})
        assert data is not None
        assert data.metrics["temperature"] == 65.0


class TestIntegration:
    @pytest.mark.asyncio
    async def test_physical_flow(self):
        config = PhysicalConfig()
        event_bus = PhysicalEventBus()
        context = PhysicalContext()
        security = PhysicalSecurityManager(config)
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context, security=security)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = RoboticsManager(manager_config)
        await manager.initialize()

        robots = await manager.get_robots()
        assert len(robots) > 0

        task = await manager.assign_task("R-001", "inspect", "Inspect product line")
        assert task.robot_id == "R-001"

        kpis = await manager.get_physical_kpis()
        assert kpis["robots_active"] > 0

        health = await manager.get_factory_health()
        assert "health_score" in health

        status = manager.get_engine_status()
        assert status["state"] == "running"

        healthy = manager.is_healthy()
        assert healthy is True

        await manager.shutdown()


if __name__ == "__main__":
    pytest.main(["-v", __file__])
