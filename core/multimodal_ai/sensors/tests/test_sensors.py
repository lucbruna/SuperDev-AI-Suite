import asyncio
import pytest
from typing import Any

from ..sensor_engine import SensorEngine, EngineState
from ..device_manager import DeviceManager
from ..telemetry import TelemetryProcessor
from ..realtime_monitor import RealtimeMonitor


@pytest.fixture
def sample_reading():
    return {
        "id": "reading-001",
        "device_id": "sensor-temp-001",
        "value": 23.5,
        "metric": "temperature",
        "unit": "celsius",
        "timestamp": "2026-07-29T12:00:00Z",
    }


@pytest.mark.asyncio
async def test_sensor_engine_initialize():
    engine = SensorEngine()
    assert engine.state == EngineState.STOPPED
    await engine.initialize()
    assert engine.state == EngineState.RUNNING
    await engine.stop()
    assert engine.state == EngineState.STOPPED


@pytest.mark.asyncio
async def test_sensor_engine_process_reading(sample_reading):
    engine = SensorEngine()
    await engine.initialize()
    result = await engine.process_reading(sample_reading)
    assert result["status"] == "processed"
    assert result["device_id"] == "sensor-temp-001"
    assert engine.metrics.readings_processed == 1
    await engine.stop()


@pytest.mark.asyncio
async def test_sensor_engine_analyze_telemetry():
    engine = SensorEngine()
    await engine.initialize()
    readings = [
        {"id": f"r-{i}", "device_id": "sensor-temp-001", "value": float(i * 10)}
        for i in range(5)
    ]
    result = await engine.analyze_telemetry(readings)
    assert result["batch_size"] == 5
    assert result["average"] == 20.0
    await engine.stop()


@pytest.mark.asyncio
async def test_sensor_engine_detect_anomalies():
    engine = SensorEngine()
    await engine.initialize()
    readings = [{"id": f"r-{i}", "device_id": "sensor-temp-001", "value": 10.0} for i in range(10)]
    readings.append({"id": "r-outlier", "device_id": "sensor-temp-001", "value": 100.0})
    anomalies = await engine.detect_anomalies(readings)
    assert len(anomalies) == 1
    assert anomalies[0]["value"] == 100.0
    await engine.stop()


@pytest.mark.asyncio
async def test_sensor_engine_get_realtime_data():
    engine = SensorEngine()
    await engine.initialize()
    data = await engine.get_realtime_data("sensor-temp-001")
    assert data["device_id"] == "sensor-temp-001"
    assert "temperature" in data
    assert "humidity" in data
    await engine.stop()


@pytest.mark.asyncio
async def test_device_manager_register_and_list():
    mgr = DeviceManager()
    devices = await mgr.list_devices()
    assert len(devices) == 3
    new_device = {"device_id": "sensor-new-001", "name": "New Sensor", "type": "temperature"}
    registered = await mgr.register_device(new_device)
    assert registered["device_id"] == "sensor-new-001"
    all_devices = await mgr.list_devices()
    assert len(all_devices) == 4
    unreg = await mgr.unregister_device("sensor-new-001")
    assert unreg is True


@pytest.mark.asyncio
async def test_device_manager_get_and_update():
    mgr = DeviceManager()
    device = await mgr.get_device("sensor-temp-001")
    assert device is not None
    assert device["name"] == "Temperature Sensor A1"
    updated = await mgr.update_device_status("sensor-temp-001", "maintenance")
    assert updated is not None
    assert updated["status"] == "maintenance"
    missing = await mgr.get_device("non-existent")
    assert missing is None


@pytest.mark.asyncio
async def test_device_manager_telemetry():
    mgr = DeviceManager()
    telemetry = await mgr.get_device_telemetry("sensor-temp-001", limit=5)
    assert len(telemetry) == 5
    assert telemetry[0]["device_id"] == "sensor-temp-001"


@pytest.mark.asyncio
async def test_telemetry_processor_process(sample_reading):
    proc = TelemetryProcessor()
    result = await proc.process_reading(sample_reading)
    assert result["reading_id"] == "reading-001"
    assert "processed_at" in result
    assert result["threshold_breach"]["breach"] is False


@pytest.mark.asyncio
async def test_telemetry_processor_threshold_breach():
    proc = TelemetryProcessor()
    reading = {"id": "r-hot", "device_id": "sensor-temp-001", "value": 100.0, "metric": "temperature"}
    result = await proc.process_reading(reading)
    assert result["threshold_breach"]["breach"] is True
    assert "outside range" in result["threshold_breach"]["message"]


@pytest.mark.asyncio
async def test_telemetry_processor_statistics():
    proc = TelemetryProcessor()
    readings = [{"value": 10.0}, {"value": 20.0}, {"value": 30.0}]
    stats = await proc.calculate_statistics(readings)
    assert stats["count"] == 3
    assert stats["mean"] == 20.0
    assert stats["min"] == 10.0
    assert stats["max"] == 30.0


@pytest.mark.asyncio
async def test_realtime_monitor_start_stop():
    monitor = RealtimeMonitor()
    health = await monitor.check_health()
    assert health["status"] == "stopped"
    await monitor.start_monitoring()
    health = await monitor.check_health()
    assert health["status"] == "healthy"
    await monitor.stop_monitoring()
    health = await monitor.check_health()
    assert health["status"] == "stopped"


@pytest.mark.asyncio
async def test_realtime_monitor_get_current_readings():
    monitor = RealtimeMonitor()
    await monitor.start_monitoring()
    await asyncio.sleep(0.1)
    readings = await monitor.get_current_readings()
    assert len(readings) > 0
    await monitor.stop_monitoring()


@pytest.mark.asyncio
async def test_realtime_monitor_subscribe():
    monitor = RealtimeMonitor()
    received_alerts: list[dict[str, Any]] = []

    def alert_cb(alert: dict[str, Any]) -> None:
        received_alerts.append(alert)

    monitor.subscribe_to_alerts(alert_cb)
    await monitor.start_monitoring()
    await asyncio.sleep(0.6)
    await monitor.stop_monitoring()

    # In normal range most samples won't trigger; test subscription works
    assert monitor._subscribers == [alert_cb]