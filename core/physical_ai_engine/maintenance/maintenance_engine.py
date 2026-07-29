from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus
from ..physical_models import FailurePrediction as FailurePredictionModel, MaintenanceRecord, MaintenanceType
from ..physical_security import PhysicalSecurityManager
from .predictive_model import PredictiveModel
from .failure_prediction import FailurePrediction
from .maintenance_scheduler import MaintenanceScheduler

logger = logging.getLogger(__name__)


class MaintenanceEngine:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext,
                 event_bus: PhysicalEventBus, security: PhysicalSecurityManager):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.security = security
        self.model: Optional[PredictiveModel] = None
        self.failure: Optional[FailurePrediction] = None
        self.scheduler: Optional[MaintenanceScheduler] = None

    async def initialize(self) -> None:
        self.model = PredictiveModel(self.config, self.context, self.event_bus)
        self.failure = FailurePrediction(self.config, self.context, self.event_bus)
        self.scheduler = MaintenanceScheduler(self.config, self.context, self.event_bus)
        logger.info("MaintenanceEngine initialized")

    async def get_schedule(self) -> List[Dict[str, Any]]:
        return self.scheduler.get_schedule()

    async def predict_failures(self, asset_id: str) -> List[FailurePredictionModel]:
        return self.failure.predict(asset_id)

    async def schedule_maintenance(self, asset_id: str, maint_type: MaintenanceType, description: str) -> MaintenanceRecord:
        return self.scheduler.schedule(asset_id, maint_type, description)

    async def get_predictive_model(self) -> Dict[str, Any]:
        return self.model.get_status()

    async def get_overdue(self) -> List[Dict[str, Any]]:
        return self.scheduler.get_overdue()

    async def shutdown(self) -> None:
        logger.info("MaintenanceEngine shutdown")
