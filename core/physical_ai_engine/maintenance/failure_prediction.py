from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus, PhysicalEvent, EventType
from ..physical_models import FailurePrediction as FailurePredictionModel

logger = logging.getLogger(__name__)


class FailurePrediction:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    def predict(self, asset_id: str) -> List[FailurePredictionModel]:
        predictions = []
        for mode in ["bearing_wear", "motor_overheating", "belt_degradation", "controller_failure"]:
            prob = hash(asset_id + mode) % 40
            if prob > 5:
                pred = FailurePredictionModel(
                    id=str(uuid.uuid4()),
                    asset_id=asset_id,
                    failure_mode=mode,
                    probability=prob / 100.0,
                    estimated_time_to_failure_hours=500 - prob * 10,
                    confidence=0.75 + (hash(mode) % 15) / 100,
                    recommended_actions=self._get_actions(mode, prob),
                )
                predictions.append(pred)
                if prob > 20:
                    import asyncio
                    asyncio.ensure_future(self.event_bus.publish(PhysicalEvent(
                        event_type=EventType.FAILURE_PREDICTED,
                        payload={"asset_id": asset_id, "mode": mode, "probability": prob},
                    )))
        return predictions

    def _get_actions(self, mode: str, prob: int) -> List[str]:
        if mode == "bearing_wear":
            return ["Inspecionar rolamentos", "Aplicar lubrificação", "Agendar substituição"]
        elif mode == "motor_overheating":
            return ["Verificar sistema de refrigeração", "Reduzir carga", "Limpar dissipadores"]
        elif mode == "belt_degradation":
            return ["Inspecionar correia", "Ajustar tensão", "Preparar substituição"]
        return ["Inspecionar equipamento", "Monitorar parâmetros"]
