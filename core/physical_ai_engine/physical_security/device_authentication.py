from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from ..physical_config import PhysicalConfig

logger = logging.getLogger(__name__)


class DeviceAuthentication:
    def __init__(self, config: PhysicalConfig):
        self._config = config
        self._credentials: Dict[str, str] = {}
        self._sessions: Dict[str, datetime] = {}

    def register(self, device_id: str, secret: str) -> None:
        hashed = hashlib.sha256(secret.encode()).hexdigest()
        self._credentials[device_id] = hashed

    def authenticate(self, device_id: str, token: str) -> bool:
        stored = self._credentials.get(device_id)
        if not stored:
            return False
        hashed = hashlib.sha256(token.encode()).hexdigest()
        if hashed == stored:
            self._sessions[device_id] = datetime.utcnow()
            return True
        return False

    def revoke(self, device_id: str) -> bool:
        self._credentials.pop(device_id, None)
        self._sessions.pop(device_id, None)
        return True

    def is_authenticated(self, device_id: str) -> bool:
        return device_id in self._sessions

    def get_active_sessions(self) -> List[str]:
        return list(self._sessions.keys())
