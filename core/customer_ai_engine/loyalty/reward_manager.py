"""
Reward Manager - Manage customer rewards and redemptions.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEvent, CustomerEventBus, EventType
from ..customer_models import Reward
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class RewardManager:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._rewards: Dict[str, List[Reward]] = {}
        self._catalog = {
            "desconto_10": {"name": "Desconto de 10%", "points_cost": 500},
            "frete_gratis": {"name": "Frete Grátis", "points_cost": 300},
            "produto_gratis": {"name": "Produto Premium Grátis", "points_cost": 2000},
            "vip_access": {"name": "Acesso VIP a Lançamentos", "points_cost": 1000},
        }

    def get_catalog(self) -> Dict[str, Any]:
        return self._catalog

    def redeem(self, customer_id: str, reward_key: str) -> Optional[Reward]:
        reward_info = self._catalog.get(reward_key)
        if not reward_info:
            return None
        reward = Reward(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            name=reward_info["name"],
            points_cost=reward_info["points_cost"],
        )
        if customer_id not in self._rewards:
            self._rewards[customer_id] = []
        self._rewards[customer_id].append(reward)
        reward.redeemed = True
        return reward

    def get_history(self, customer_id: str) -> List[Reward]:
        return self._rewards.get(customer_id, [])
