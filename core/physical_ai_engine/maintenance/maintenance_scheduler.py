from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus, PhysicalEvent, EventType
from ..physical_models import MaintenanceRecord, MaintenanceType

logger = logging.getLogger(__name__)


class MaintenanceScheduler:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._records: Dict[str, MaintenanceRecord] = {}
        self._init_records()

    def _init_records(self) -> None:
        assets = ["M-001", "M-002", "M-003", "R-001", "R-002"]
        for asset_id in assets:
            record = MaintenanceRecord(
                id=str(uuid.uuid4()),
                asset_id=asset_id,
                maintenance_type=MaintenanceType.PREVENTIVE,
                description=f"Manutenção preventiva - {asset_id}",
                scheduled_date=datetime.utcnow() + timedelta(days=30),
                status="scheduled",
            )
            self._records[record.id] = record

    def schedule(self, asset_id: str, maint_type: MaintenanceType, description: str) -> MaintenanceRecord:
        record = MaintenanceRecord(
            id=str(uuid.uuid4()),
            asset_id=asset_id,
            maintenance_type=maint_type,
            description=description,
            scheduled_date=datetime.utcnow() + timedelta(days=7),
            status="scheduled",
        )
        self._records[record.id] = record
        return record

    def complete(self, record_id: str) -> Optional[MaintenanceRecord]:
        record = self._records.get(record_id)
        if not record:
            return None
        record.status = "completed"
        record.completed_date = datetime.utcnow()
        return record

    def get_schedule(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": r.id,
                "asset_id": r.asset_id,
                "type": r.maintenance_type.value,
                "description": r.description,
                "scheduled_date": r.scheduled_date.isoformat() if r.scheduled_date else "",
                "status": r.status,
            }
            for r in self._records.values()
        ]

    def get_overdue(self) -> List[Dict[str, Any]]:
        now = datetime.utcnow()
        return [
            {"id": r.id, "asset_id": r.asset_id, "description": r.description}
            for r in self._records.values()
            if r.scheduled_date and r.scheduled_date < now and r.status == "scheduled"
        ]

    def get_by_asset(self, asset_id: str) -> List[MaintenanceRecord]:
        return [r for r in self._records.values() if r.asset_id == asset_id]
