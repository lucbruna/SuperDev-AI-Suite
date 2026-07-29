"""
Input Processor - Detects modality and routes to correct handler.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from .multimodal_config import MultimodalConfig
from .multimodal_models import (
    InputType, OutputType, MultimodalInput, MultimodalOutput,
    ProcessedInput, UnderstandingResult,
)
from ._engine_types import EngineConfig
from .multimodal_security import MultimodalSecurityManager

logger = logging.getLogger(__name__)


class InputProcessor:
    def __init__(self, config: EngineConfig, security: MultimodalSecurityManager):
        self._config = config
        self._security = security
        self._text_handlers = {
            "sentiment": self._analyze_sentiment,
            "entities": self._extract_entities,
            "summarize": self._summarize_text,
        }
        self._sensor_mappings = {
            "temperature": "temperature_celsius",
            "humidity": "humidity_percent",
            "pressure": "pressure_hpa",
            "motion": "motion_detected",
            "light": "light_lux",
            "audio_level": "audio_level_db",
            "proximity": "proximity_cm",
        }

    async def process(self, inp: MultimodalInput) -> ProcessedInput:
        start = time.perf_counter()
        sanitized = self._security.sanitize_input(str(inp.data)) if isinstance(inp.data, str) else inp.data
        result = ProcessedInput(input_id=inp.id, original_type=inp.type)
        try:
            if inp.type == InputType.TEXT:
                result = await self.process_text(sanitized, inp)
            elif inp.type == InputType.VOICE:
                result = await self.process_voice(sanitized, inp)
            elif inp.type == InputType.IMAGE:
                result = await self.process_image(sanitized, inp)
            elif inp.type == InputType.VIDEO:
                result = await self.process_video(sanitized, inp)
            elif inp.type == InputType.DOCUMENT:
                result = await self.process_document(sanitized, inp)
            elif inp.type == InputType.SENSOR:
                result = await self.process_sensor_data(sanitized, inp)
            else:
                result = await self.process_text(str(sanitized), inp)
        except Exception as e:
            logger.error(f"Error processing {inp.type.value}: {e}")
            result.confidence = 0.0
            result.features = {"error": str(e)}
        result.processing_time_ms = (time.perf_counter() - start) * 1000
        return result

    async def detect_modality(self, data: Any, mime_type: Optional[str] = None) -> InputType:
        if mime_type:
            if mime_type.startswith("text/"):
                return InputType.TEXT
            if mime_type.startswith("audio/"):
                return InputType.VOICE
            if mime_type.startswith("image/"):
                return InputType.IMAGE
            if mime_type.startswith("video/"):
                return InputType.VIDEO
            if mime_type in ("application/pdf", "application/msword",
                             "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                             "text/csv", "application/vnd.ms-excel"):
                return InputType.DOCUMENT
        if isinstance(data, str):
            return InputType.TEXT
        if isinstance(data, bytes):
            if mime_type:
                return self.detect_modality(data, mime_type)
            return InputType.DOCUMENT
        if isinstance(data, dict):
            sensor_keys = {"temperature", "humidity", "pressure", "motion", "light", "audio_level", "proximity"}
            if sensor_keys & set(data.keys()):
                return InputType.SENSOR
        return InputType.TEXT

    async def process_text(self, data: Any, inp: MultimodalInput) -> ProcessedInput:
        text = str(data) if not isinstance(data, str) else data
        tokens = text.split()
        result = ProcessedInput(
            input_id=inp.id,
            original_type=InputType.TEXT,
            normalized_text=text.lower().strip(),
            tokens=tokens,
            detected_language=inp.language or self._detect_language(text),
            confidence=1.0,
        )
        result.features = {
            "char_count": len(text),
            "word_count": len(tokens),
            "has_questions": "?" in text,
            "has_exclamations": "!" in text,
            "all_caps_ratio": sum(1 for w in tokens if w.isupper()) / max(len(tokens), 1),
        }
        return result

    async def process_voice(self, data: Any, inp: MultimodalInput) -> ProcessedInput:
        text = str(data) if not isinstance(data, str) else data
        result = ProcessedInput(
            input_id=inp.id,
            original_type=InputType.VOICE,
            normalized_text=text.lower().strip(),
            tokens=text.split(),
            detected_language=inp.language or self._detect_language(text),
            confidence=0.85,
        )
        result.features = {
            "duration_seconds": inp.metadata.get("duration_seconds", 0),
            "sample_rate": inp.metadata.get("sample_rate", 16000),
            "has_transcript": bool(text),
        }
        return result

    async def process_image(self, data: Any, inp: MultimodalInput) -> ProcessedInput:
        result = ProcessedInput(
            input_id=inp.id,
            original_type=InputType.IMAGE,
            confidence=0.9,
        )
        result.features = {
            "width": inp.metadata.get("width", 0),
            "height": inp.metadata.get("height", 0),
            "format": inp.mime_type or "unknown",
            "file_size_bytes": len(inp.raw_bytes) if inp.raw_bytes else 0,
            "has_metadata": bool(inp.metadata),
        }
        return result

    async def process_video(self, data: Any, inp: MultimodalInput) -> ProcessedInput:
        result = ProcessedInput(
            input_id=inp.id,
            original_type=InputType.VIDEO,
            confidence=0.85,
        )
        result.features = {
            "duration_seconds": inp.metadata.get("duration_seconds", 0),
            "format": inp.mime_type or "unknown",
            "file_size_bytes": len(inp.raw_bytes) if inp.raw_bytes else 0,
            "frame_count": inp.metadata.get("frame_count", 0),
            "has_audio": inp.metadata.get("has_audio", False),
        }
        return result

    async def process_document(self, data: Any, inp: MultimodalInput) -> ProcessedInput:
        text = str(data) if not isinstance(data, str) else data
        tokens = text.split()
        result = ProcessedInput(
            input_id=inp.id,
            original_type=InputType.DOCUMENT,
            normalized_text=text.lower().strip(),
            tokens=tokens,
            detected_language=inp.language or self._detect_language(text),
            confidence=0.95,
        )
        result.features = {
            "mime_type": inp.mime_type or "unknown",
            "page_count": inp.metadata.get("page_count", 1),
            "char_count": len(text),
            "word_count": len(tokens),
        }
        return result

    async def process_sensor_data(self, data: Any, inp: MultimodalInput) -> ProcessedInput:
        readings = data if isinstance(data, dict) else {}
        result = ProcessedInput(
            input_id=inp.id,
            original_type=InputType.SENSOR,
            confidence=0.95,
        )
        parsed = {}
        for alias, key in self._sensor_mappings.items():
            if alias in readings:
                parsed[key] = readings[alias]
        parsed.update({k: v for k, v in readings.items() if k not in self._sensor_mappings})
        result.features = {
            "readings": parsed,
            "reading_count": len(parsed),
            "timestamp": inp.metadata.get("sensor_timestamp", ""),
            "source": inp.metadata.get("sensor_id", "unknown"),
        }
        return result

    def _detect_language(self, text: str) -> str:
        if not text.strip():
            return "unknown"
        text_lower = text.lower()
        portuguese_words = {"a", "o", "de", "da", "do", "em", "para", "com", "que", "é", "não", "um", "uma", "os", "as"}
        english_words = {"the", "is", "are", "and", "for", "with", "this", "that", "from", "have", "not"}
        words = set(text_lower.split())
        pt_count = len(words & portuguese_words)
        en_count = len(words & english_words)
        if pt_count > en_count:
            return "pt"
        return "en"

    def _analyze_sentiment(self, text: str) -> float:
        positive = {"good", "great", "excellent", "happy", "love", "wonderful", "amazing", "fantastic",
                    "awesome", "perfect", "beautiful", "pleased", "satisfied", "grateful", "thankful"}
        negative = {"bad", "terrible", "awful", "hate", "horrible", "angry", "upset", "sad",
                    "frustrated", "annoyed", "disappointed", "worst", "poor", "ugly", "awful"}
        words = set(text.lower().split())
        pos_count = len(words & positive)
        neg_count = len(words & negative)
        total = pos_count + neg_count
        if total == 0:
            return 0.5
        return pos_count / total

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        import re
        entities: Dict[str, List[str]] = {}
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        emails = re.findall(email_pattern, text)
        if emails:
            entities["email"] = emails
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        if urls:
            entities["url"] = urls
        number_pattern = r'\b\d+\.?\d*\b'
        numbers = re.findall(number_pattern, text)
        if numbers:
            entities["numbers"] = numbers[:10]
        return entities

    def _summarize_text(self, text: str, max_sentences: int = 3) -> str:
        import re
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        if not sentences:
            return text[:200]
        return " ".join(sentences[:max_sentences]) + "."
