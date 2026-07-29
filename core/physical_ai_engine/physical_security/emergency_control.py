from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig

logger = logging.getLogger(__name__)


class EmergencyControl:
    def __init__(self, config: PhysicalConfig):
        self._config = config
        self._active = False
        self._history: List[Dict[str, Any]] = []
        self._active_stop_id: Optional[str] = None

    def trigger(self, source: str, reason: str) -> Dict[str, Any]:
        stop_id = str(uuid.uuid4())
        entry = {
            "id": stop_id,
            "source": source,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "resolved": False,
        }
        self._history.append(entry)
        self._active = True
        self._active_stop_id = stop_id
        logger.critical(f"EMERGENCY STOP triggered by {source}: {reason}")
        return entry

    def reset(self) -> bool:
        if self._active_stop_id:
            for entry in self._history:
                if entry["id"] == self._active_stop_id:
                    entry["resolved"] = True
                    entry["resolved_at"] = datetime.utcnow().isoformat()
        self._active = False
        self._active_stop_id = None
        logger.info("Emergency stop reset")
        return True

    def is_active(self) -> bool:
        return self._active

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._history[-limit:]
