"""
Security Monitor - Real-time security monitoring and alerting.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..supply_config import SupplyChainConfig

logger = logging.getLogger(__name__)


class SecurityMonitor:
    def __init__(self, config: SupplyChainConfig):
        self.config = config
        self._alerts: List[Dict[str, Any]] = []
        self._suspicious_activities: List[Dict[str, Any]] = []

    async def monitor_access(self, user_id: str, resource: str, action: str, allowed: bool) -> Optional[Dict[str, Any]]:
        if not allowed:
            alert = {
                "type": "access_denied",
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "timestamp": datetime.utcnow().isoformat(),
                "severity": "medium",
            }
            self._suspicious_activities.append(alert)
            logger.warning(f"Access denied: {user_id} tried {action} on {resource}")
            return alert
        return None

    async def detect_anomalies(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        anomalies = []
        for tx in transactions:
            if tx.get("value", 0) > 100000:
                anomalies.append({
                    "type": "high_value_transaction",
                    "transaction_id": tx.get("id"),
                    "value": tx.get("value"),
                    "severity": "high",
                })
        self._alerts.extend(anomalies)
        return anomalies

    async def get_security_status(self) -> Dict[str, Any]:
        return {
            "active_alerts": len(self._alerts),
            "suspicious_activities": len(self._suspicious_activities),
            "last_incident": self._alerts[-1]["timestamp"] if self._alerts else None,
            "security_score": 92,
            "recommendations": [
                "Revisar permissões de usuários inativos",
                "Atualizar senhas de fornecedores",
            ],
        }