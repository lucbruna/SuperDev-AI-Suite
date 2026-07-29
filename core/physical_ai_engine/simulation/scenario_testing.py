from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus

logger = logging.getLogger(__name__)


class ScenarioTesting:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    def run(self, scenario: Dict[str, Any]) -> List[str]:
        issues = []
        speed = scenario.get("speed", 0)
        temperature = scenario.get("temperature", 25)
        load = scenario.get("load", 0)

        if speed > 100:
            issues.append("Velocidade acima do limite seguro")
        if temperature > 85:
            issues.append("Temperatura crítica - risco de superaquecimento")
        if load > 500:
            issues.append("Carga excessiva para o equipamento")
        if speed < 0:
            issues.append("Velocidade negativa inválida")

        return issues

    def validate_parameters(self, scenario: Dict[str, Any]) -> List[str]:
        errors = []
        required = ["name", "cycles", "duration"]
        for field in required:
            if field not in scenario:
                errors.append(f"Campo obrigatório: {field}")
        return errors
