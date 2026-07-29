from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus, PhysicalEvent, EventType

logger = logging.getLogger(__name__)


class StateSync:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._sync_log: List[Dict[str, Any]] = []

    async def sync(self, asset_id: str) -> bool:
        logger.info(f"Syncing digital twin for {asset_id}")
        await asyncio.sleep(0.05)
        self._sync_log.append({
            "asset_id": asset_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "synced",
        })
        await self.event_bus.publish(PhysicalEvent(
            event_type=EventType.TWIN_SYNCED,
            payload={"asset_id": asset_id, "status": "synced"},
        ))
        return True

    async def sync_all(self, asset_ids: List[str]) -> Dict[str, bool]:
        results = {}
        for aid in asset_ids:
            results[aid] = await self.sync(aid)
        return results

    def get_sync_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._sync_log[-limit:]
