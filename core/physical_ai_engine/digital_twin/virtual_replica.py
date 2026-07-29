from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus
from ..physical_models import DigitalTwin

logger = logging.getLogger(__name__)


class VirtualReplica:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._twins: Dict[str, DigitalTwin] = {}
        self._init_twins()

    def _init_twins(self) -> None:
        for asset_id in ["M-001", "M-002", "M-003", "R-001", "R-002"]:
            self._twins[asset_id] = DigitalTwin(
                id=str(uuid.uuid4()),
                asset_id=asset_id,
                asset_type="machine" if asset_id.startswith("M") else "robot",
                name=f"Twin-{asset_id}",
                state={"status": "running", "temperature": 65.0, "uptime": 1200},
                health_score=92.5,
            )

    def get(self, asset_id: str) -> Optional[Dict[str, Any]]:
        twin = self._twins.get(asset_id)
        if not twin:
            return None
        return {
            "id": twin.id,
            "asset_id": twin.asset_id,
            "asset_type": twin.asset_type,
            "name": twin.name,
            "state": twin.state,
            "health_score": twin.health_score,
            "last_sync": twin.last_sync,
        }

    def get_all(self) -> List[Dict[str, Any]]:
        return [self.get(aid) for aid in self._twins if self.get(aid)]

    def create(self, asset_id: str, asset_type: str, name: str) -> DigitalTwin:
        twin = DigitalTwin(
            id=str(uuid.uuid4()),
            asset_id=asset_id,
            asset_type=asset_type,
            name=name,
            state={"status": "created"},
        )
        self._twins[asset_id] = twin
        return twin

    def update_state(self, asset_id: str, state: Dict[str, Any]) -> Optional[DigitalTwin]:
        twin = self._twins.get(asset_id)
        if twin:
            twin.state.update(state)
            twin.last_sync = datetime.utcnow()
        return twin

    def update_health(self, asset_id: str, score: float) -> Optional[DigitalTwin]:
        twin = self._twins.get(asset_id)
        if twin:
            twin.health_score = score
        return twin
