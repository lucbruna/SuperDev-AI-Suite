"""
Output Generator - Generates multimodal responses from processed input.
"""

from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .multimodal_config import MultimodalConfig
from .multimodal_models import (
    InputType, OutputType, ModalityType,
    MultimodalInput, MultimodalOutput, ProcessedInput,
    InteractionSession,
)
from ._engine_types import EngineConfig
from .multimodal_security import MultimodalSecurityManager

logger = logging.getLogger(__name__)


class OutputGenerator:
    def __init__(self, config: EngineConfig, security: MultimodalSecurityManager):
        self._config = config
        self._security = security

    async def generate(
        self,
        processed: ProcessedInput,
        session: Optional[InteractionSession] = None,
    ) -> MultimodalOutput:
        start = time.perf_counter()
        output_type = await self.select_output_modality(processed, session)
        content = None
        if output_type == OutputType.TEXT:
            content = await self.generate_text(processed)
        elif output_type == OutputType.VOICE:
            content = await self.generate_voice(processed)
        elif output_type == OutputType.IMAGE_DESCRIPTION:
            content = await self.generate_image_description(processed)
        elif output_type == OutputType.DOCUMENT_SUMMARY:
            content = await self.generate_document_summary(processed)
        elif output_type == OutputType.STRUCTURED_DATA:
            content = await self.format_response(processed, "json")
        else:
            content = await self.generate_text(processed)
        formatted = await self.format_response_content(content, output_type)
        elapsed = (time.perf_counter() - start) * 1000
        return MultimodalOutput(
            id=str(uuid.uuid4()),
            input_id=processed.input_id,
            type=output_type,
            content=formatted,
            confidence=processed.confidence,
            processing_time_ms=elapsed,
            metadata={"original_type": processed.original_type.value},
        )

    async def select_output_modality(
        self,
        processed: ProcessedInput,
        session: Optional[InteractionSession] = None,
    ) -> OutputType:
        input_type = processed.original_type
        if input_type == InputType.TEXT:
            return OutputType.TEXT
        if input_type == InputType.VOICE:
            return OutputType.TEXT
        if input_type == InputType.IMAGE:
            return OutputType.IMAGE_DESCRIPTION
        if input_type == InputType.VIDEO:
            return OutputType.IMAGE_DESCRIPTION
        if input_type == InputType.DOCUMENT:
            return OutputType.DOCUMENT_SUMMARY
        if input_type == InputType.SENSOR:
            return OutputType.STRUCTURED_DATA
        return OutputType.TEXT

    async def generate_text(self, processed: ProcessedInput) -> str:
        text = processed.normalized_text or ""
        if not text:
            return "No text content available."
        sentiment = self._assess_sentiment(text)
        response = self._build_response(text, sentiment)
        return self._security.sanitize_input(response)

    async def generate_voice(self, processed: ProcessedInput) -> str:
        text = processed.normalized_text or ""
        if not text:
            return ""
        response = self._build_response(text, "neutral")
        return response

    async def generate_image_description(self, processed: ProcessedInput) -> str:
        features = processed.features
        width = features.get("width", 0)
        height = features.get("height", 0)
        fmt = features.get("format", "unknown")
        size_kb = features.get("file_size_bytes", 0) / 1024
        desc = f"Image ({fmt}, {width}x{height}, {size_kb:.1f}KB)"
        if width and height:
            desc += f". Aspect ratio: {width/height:.2f}"
        return desc

    async def generate_document_summary(self, processed: ProcessedInput) -> str:
        text = processed.normalized_text or ""
        features = processed.features
        word_count = features.get("word_count", 0)
        page_count = features.get("page_count", 1)
        summary = f"Document summary: {word_count} words across {page_count} page(s)."
        if text:
            first_sentence = text.split(".")[0] if "." in text else text[:100]
            summary += f" Preview: {first_sentence.strip()[:200]}."
        return summary

    async def format_response(self, processed: ProcessedInput, fmt: str = "text") -> Any:
        data = {
            "input_id": processed.input_id,
            "type": processed.original_type.value,
            "confidence": processed.confidence,
            "features": processed.features,
            "detected_language": processed.detected_language,
            "processing_time_ms": processed.processing_time_ms,
        }
        if fmt == "json":
            return data
        if fmt == "text":
            lines = [f"{k}: {v}" for k, v in data.items() if not isinstance(v, dict)]
            return "\n".join(lines)
        return data

    async def format_response_content(self, content: Any, output_type: OutputType) -> Any:
        if isinstance(content, str):
            return content
        if isinstance(content, dict):
            return content
        return str(content)

    def _assess_sentiment(self, text: str) -> str:
        positive = {"good", "great", "excellent", "happy", "love", "wonderful", "amazing",
                    "fantastic", "awesome", "perfect", "beautiful", "pleased", "satisfied"}
        negative = {"bad", "terrible", "awful", "hate", "horrible", "angry", "upset", "sad",
                    "frustrated", "annoyed", "disappointed", "worst"}
        words = set(text.lower().split())
        pos = len(words & positive)
        neg = len(words & negative)
        if pos > neg:
            return "positive"
        if neg > pos:
            return "negative"
        return "neutral"

    def _build_response(self, text: str, sentiment: str) -> str:
        if sentiment == "positive":
            prefix = "I'm glad to hear that! "
        elif sentiment == "negative":
            prefix = "I understand your concern. "
        else:
            prefix = ""
        if "?" in text:
            return prefix + self._answer_question(text)
        return prefix + self._generate_reply(text)

    def _answer_question(self, text: str) -> str:
        text_lower = text.lower()
        if "how are you" in text_lower:
            return "I'm functioning well, thank you for asking! How can I assist you today?"
        if "what" in text_lower and "your name" in text_lower:
            return "I'm the Multimodal AI Engine, your intelligent assistant."
        if "who" in text_lower and "you" in text_lower:
            return "I'm an AI assistant capable of processing text, voice, images, video, documents, and sensor data."
        if "help" in text_lower:
            return "I can help you with information, analysis, and processing across multiple modalities. What would you like to do?"
        return "That's an interesting question. Let me process that for you."

    def _generate_reply(self, text: str) -> str:
        text_lower = text.lower()
        if "hello" in text_lower or "hi" in text_lower or "hey" in text_lower:
            return "Hello! How can I assist you today?"
        if "thank" in text_lower:
            return "You're welcome! Is there anything else I can help you with?"
        if "bye" in text_lower or "goodbye" in text_lower:
            return "Goodbye! Feel free to come back anytime."
        if "yes" in text_lower:
            return "Great! What would you like to know?"
        if "no" in text_lower:
            return "No problem. Let me know if you need anything else."
        return f"I received your message. I'm processing it using my multimodal capabilities."
