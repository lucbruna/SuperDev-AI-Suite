"""
Speech Recognition - Transcribe audio to text (simulation interface).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class SpeechRecognition:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._language = config.voice.stt_language

    def transcribe(self, audio_data: bytes) -> str:
        if not audio_data:
            return ""
        return "[Transcrição de áudio processada]"

    def detect_language(self, audio_data: bytes) -> str:
        return self._language

    def get_supported_languages(self) -> List[str]:
        return ["pt-BR", "en-US", "es-ES"]
