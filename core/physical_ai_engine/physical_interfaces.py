from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .physical_models import Robot, Device, SensorReading, TelemetryData

logger = logging.getLogger(__name__)


class RobotInterface(ABC):
    @abstractmethod
    async def connect(self, robot_id: str) -> bool: ...

    @abstractmethod
    async def disconnect(self, robot_id: str) -> bool: ...

    @abstractmethod
    async def send_command(self, robot_id: str, command: str, params: Dict[str, Any]) -> Dict[str, Any]: ...

    @abstractmethod
    async def get_status(self, robot_id: str) -> Robot: ...

    @abstractmethod
    async def emergency_stop(self, robot_id: str) -> bool: ...


class DeviceInterface(ABC):
    @abstractmethod
    async def register_device(self, device: Device) -> bool: ...

    @abstractmethod
    async def read_data(self, device_id: str) -> Dict[str, Any]: ...

    @abstractmethod
    async def write_data(self, device_id: str, data: Dict[str, Any]) -> bool: ...

    @abstractmethod
    async def ping(self, device_id: str) -> bool: ...


class SensorInterface(ABC):
    @abstractmethod
    async def read_sensor(self, sensor_id: str) -> SensorReading: ...

    @abstractmethod
    async def calibrate(self, sensor_id: str) -> bool: ...

    @abstractmethod
    async def get_readings(self, sensor_id: str, count: int = 10) -> List[SensorReading]: ...


class SimulationInterface(ABC):
    @abstractmethod
    async def start_simulation(self, scenario: Dict[str, Any]) -> str: ...

    @abstractmethod
    async def stop_simulation(self, sim_id: str) -> bool: ...

    @abstractmethod
    async def get_simulation_status(self, sim_id: str) -> Dict[str, Any]: ...


class ConcreteRobotInterface(RobotInterface):
    async def connect(self, robot_id: str) -> bool:
        logger.info(f"Connecting to robot {robot_id}")
        return True

    async def disconnect(self, robot_id: str) -> bool:
        logger.info(f"Disconnecting robot {robot_id}")
        return True

    async def send_command(self, robot_id: str, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Command {command} to {robot_id}")
        return {"status": "executed", "command": command}

    async def get_status(self, robot_id: str) -> Robot:
        return Robot(id=robot_id, name=f"Robot-{robot_id}")

    async def emergency_stop(self, robot_id: str) -> bool:
        logger.warning(f"EMERGENCY STOP: {robot_id}")
        return True


class ConcreteDeviceInterface(DeviceInterface):
    async def register_device(self, device: Device) -> bool:
        logger.info(f"Registered device {device.id}")
        return True

    async def read_data(self, device_id: str) -> Dict[str, Any]:
        return {"device_id": device_id, "value": 42.0}

    async def write_data(self, device_id: str, data: Dict[str, Any]) -> bool:
        logger.info(f"Written to {device_id}: {data}")
        return True

    async def ping(self, device_id: str) -> bool:
        return True


class ConcreteSensorInterface(SensorInterface):
    async def read_sensor(self, sensor_id: str) -> SensorReading:
        return SensorReading(id=sensor_id, sensor_id=sensor_id, value=25.0)

    async def calibrate(self, sensor_id: str) -> bool:
        logger.info(f"Calibrated sensor {sensor_id}")
        return True

    async def get_readings(self, sensor_id: str, count: int = 10) -> List[SensorReading]:
        return [SensorReading(id=f"{sensor_id}-{i}", sensor_id=sensor_id, value=25.0 + i) for i in range(count)]


class ConcreteSimulationInterface(SimulationInterface):
    async def start_simulation(self, scenario: Dict[str, Any]) -> str:
        sim_id = f"sim-{hash(str(scenario))}"
        logger.info(f"Started simulation {sim_id}")
        return sim_id

    async def stop_simulation(self, sim_id: str) -> bool:
        logger.info(f"Stopped simulation {sim_id}")
        return True

    async def get_simulation_status(self, sim_id: str) -> Dict[str, Any]:
        return {"id": sim_id, "status": "running", "progress": 65.0}
