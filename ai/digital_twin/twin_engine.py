"""Digital Twin engine — main orchestrator."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from .twin_config import TwinConfig
from .twin_models import DigitalEntity, SimulationConfig, SimulationResult, ScenarioConfig
from .twin_events import TwinEvents
from .twin_metrics import TwinMetrics
from .twin_logger import TwinLogger

class TwinEngine:
    def __init__(self, config: TwinConfig = None) -> None:
        self._config = config or TwinConfig()
        self._events = TwinEvents()
        self._metrics = TwinMetrics()
        self._logger = TwinLogger()
        self._entities: Dict[str, DigitalEntity] = {}
        self._simulations: Dict[str, SimulationConfig] = {}
        self._scenarios: Dict[str, Dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
        self._events.emit("engine.started")
        self._logger.info("TwinEngine started")
    def stop(self) -> None:
        self._started = False
        self._events.emit("engine.stopped")
    def create_entity(self, name: str, entity_type: str = "generic", attributes: Dict[str, Any] = None) -> DigitalEntity:
        entity = DigitalEntity(name=name, entity_type=entity_type, attributes=attributes or {})
        self._entities[entity.entity_id] = entity
        self._metrics.increment("entities_created")
        self._events.emit("entity.created", {"entity_id": entity.entity_id})
        return entity
    def get_entity(self, entity_id: str) -> Optional[DigitalEntity]:
        return self._entities.get(entity_id)
    def update_entity(self, entity_id: str, attributes: Dict[str, Any]) -> bool:
        entity = self._entities.get(entity_id)
        if not entity:
            return False
        entity.attributes.update(attributes)
        entity.updated_at = __import__("time").time()
        return True
    def delete_entity(self, entity_id: str) -> bool:
        if entity_id in self._entities:
            del self._entities[entity_id]
            return True
        return False
    def list_entities(self, entity_type: str = "") -> List[DigitalEntity]:
        if entity_type:
            return [e for e in self._entities.values() if e.entity_type == entity_type]
        return list(self._entities.values())
    def create_simulation(self, name: str, time_steps: int = 100) -> SimulationConfig:
        sim = SimulationConfig(name=name, time_steps=time_steps)
        self._simulations[sim.simulation_id] = sim
        self._metrics.increment("simulations_created")
        return sim
    def run_simulation(self, sim_id: str) -> SimulationResult:
        sim = self._simulations.get(sim_id)
        if not sim:
            return SimulationResult(state=__import__("digital_twin.twin_models", fromlist=["SimulationState"]).SimulationState.FAILED)
        import time
        start = time.time()
        sim.state = __import__("digital_twin.twin_models", fromlist=["SimulationState"]).SimulationState.RUNNING
        events = []
        for step in range(sim.time_steps):
            events.append({"step": step, "time": step * sim.dt})
        duration = time.time() - start
        sim.state = __import__("digital_twin.twin_models", fromlist=["SimulationState"]).SimulationState.COMPLETED
        result = SimulationResult(simulation_id=sim_id, state=sim.state, events=events, duration_seconds=duration, metrics={"steps": sim.time_steps})
        self._metrics.increment("simulations_completed")
        self._events.emit("simulation.completed", {"sim_id": sim_id})
        return result
    def create_scenario(self, name: str, parameters: Dict[str, Any] = None) -> ScenarioConfig:
        scenario = ScenarioConfig(name=name, parameters=parameters or {})
        self._scenarios[scenario.scenario_id] = {"config": scenario, "results": []}
        self._metrics.increment("scenarios_created")
        return scenario
    def get_metrics(self) -> Dict[str, Any]:
        return self._metrics.summary()
    def get_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._events.get_log(limit=limit)
    def is_running(self) -> bool:
        return self._started
    def entity_count(self) -> int:
        return len(self._entities)
    def simulation_count(self) -> int:
        return len(self._simulations)
    def scenario_count(self) -> int:
        return len(self._scenarios)
