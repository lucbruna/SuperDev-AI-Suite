"""
Voice Response - Synthesize text to speech responses.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class VoiceResponse:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    def synthesize(self, text: str) -> bytes:
        if not text:
            return b""
        return text.encode("utf-8")

    def get_available_voices(self) -> List[str]:
        return ["default", "female_1", "male_1"]
