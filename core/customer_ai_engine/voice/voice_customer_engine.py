"""
Voice Customer Engine - Process voice calls with speech recognition.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEvent, CustomerEventBus, EventType
from ..customer_models import CallRecord, SentimentType, ChannelType
from ..customer_config import CustomerConfig
from .speech_recognition import SpeechRecognition
from .voice_response import VoiceResponse
from .call_manager import CallManager

logger = logging.getLogger(__name__)


class VoiceCustomerEngine:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.recognizer: Optional[SpeechRecognition] = None
        self.responder: Optional[VoiceResponse] = None
        self.calls: Optional[CallManager] = None

    async def initialize(self) -> None:
        self.recognizer = SpeechRecognition(self.config, self.context, self.event_bus)
        self.responder = VoiceResponse(self.config, self.context, self.event_bus)
        self.calls = CallManager(self.config, self.context, self.event_bus)
        logger.info("VoiceCustomerEngine initialized")

    async def handle_incoming(self, caller_number: str) -> CallRecord:
        record = self.calls.create(caller_number)
        await self.event_bus.publish(CustomerEvent(
            event_type=EventType.CALL_RECEIVED,
            payload={"call_id": record.id, "caller": caller_number},
        ))
        return record

    async def process_audio(self, call_id: str, audio_data: bytes) -> str:
        call = self.calls.get(call_id)
        if not call:
            return ""
        text = self.recognizer.transcribe(audio_data)
        call.transcript += " " + text
        return text

    async def generate_response(self, call_id: str, text: str) -> bytes:
        response = self.responder.synthesize(text)
        return response

    async def end_call(self, call_id: str) -> CallRecord:
        call = self.calls.end(call_id)
        await self.event_bus.publish(CustomerEvent(
            event_type=EventType.CALL_ENDED,
            payload={"call_id": call_id, "duration": call.duration_seconds},
        ))
        return call

    async def shutdown(self) -> None:
        logger.info("VoiceCustomerEngine shutdown")
