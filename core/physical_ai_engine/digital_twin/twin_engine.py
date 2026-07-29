from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus
from ..physical_models import DigitalTwin
from ..physical_security import PhysicalSecurityManager
from .virtual_replica import VirtualReplica
from .state_sync import StateSync
from .prediction import TwinPrediction

logger = logging.getLogger(__name__)


class TwinEngine:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext,
                 event_bus: PhysicalEventBus, security: PhysicalSecurityManager):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.security = security
        self.replica: Optional[VirtualReplica] = None
        self.sync: Optional[StateSync] = None
        self.prediction: Optional[TwinPrediction] = None

    async def initialize(self) -> None:
        self.replica = VirtualReplica(self.config, self.context, self.event_bus)
        self.sync = StateSync(self.config, self.context, self.event_bus)
        self.prediction = TwinPrediction(self.config, self.context, self.event_bus)
        logger.info("TwinEngine initialized")

    async def get(self, asset_id: str) -> Optional[Dict[str, Any]]:
        twin = self.replica.get(asset_id)
        if not twin:
            return None
        predictions = self.prediction.predict(asset_id)
        return {**twin, "predictions": predictions}

    async def get_all(self) -> List[Dict[str, Any]]:
        return self.replica.get_all()

    async def sync_asset(self, asset_id: str) -> bool:
        return await self.sync.sync(asset_id)

    async def get_predictions(self, asset_id: str) -> Dict[str, Any]:
        return self.prediction.predict(asset_id)

    async def create_twin(self, asset_id: str, asset_type: str, name: str) -> DigitalTwin:
        return self.replica.create(asset_id, asset_type, name)

    async def shutdown(self) -> None:
        logger.info("TwinEngine shutdown")
