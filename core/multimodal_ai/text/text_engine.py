from typing import Any, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class EngineConfig:
    language: str = "en"
    max_tokens: int = 4096
    temperature: float = 0.7
    enable_sentiment: bool = True
    enable_entity_extraction: bool = True
    cache_enabled: bool = True


@dataclass
class EngineState:
    status: str = "idle"
    started_at: Optional[datetime] = None
    last_processed: Optional[datetime] = None
    error_count: int = 0

    def start(self) -> None:
        self.status = "running"
        self.started_at = datetime.now()

    def stop(self) -> None:
        self.status = "stopped"

    def record_error(self) -> None:
        self.error_count += 1


@dataclass
class EngineMetrics:
    texts_processed: int = 0
    total_processing_time: float = 0.0
    average_confidence: float = 0.0
    intents_detected: int = 0
    tokens_consumed: int = 0

    def record_processing(self, time: float, confidence: float, tokens: int) -> None:
        self.texts_processed += 1
        self.total_processing_time += time
        self.intents_detected += 1
        self.tokens_consumed += tokens
        self.average_confidence = (
            (self.average_confidence * (self.texts_processed - 1) + confidence)
            / self.texts_processed
        )


class TextEngine:
    def __init__(self, config: Optional[EngineConfig] = None) -> None:
        self.config = config or EngineConfig()
        self.state = EngineState()
        self.metrics = EngineMetrics()
        from .language_processor import LanguageProcessor
        from .intent_detection import IntentDetector
        from .semantic_analysis import SemanticAnalyzer
        from .text_generation import TextGenerator
        self.language_processor = LanguageProcessor()
        self.intent_detection = IntentDetector()
        self.semantic_analysis = SemanticAnalyzer()
        self.text_generation = TextGenerator()

    async def process_text(self, text: str, options: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        import time
        self.state.start()
        start = time.time()
        tokens = len(text.split())

        syntax = self.language_processor.analyze_syntax(text)
        language = self.language_processor.detect_language(text)
        entities = self.language_processor.extract_entities(text) if self.config.enable_entity_extraction else []
        intent = self.intent_detection.detect_intent(text)
        confidence = self.intent_detection.get_confidence(text, intent)
        params = self.intent_detection.extract_parameters(text)
        semantics = self.semantic_analysis.analyze_semantics(text) if self.config.enable_sentiment else {}

        elapsed = time.time() - start
        self.metrics.record_processing(elapsed, confidence, tokens)

        result = {
            "text": text,
            "syntax": syntax,
            "language": language,
            "entities": entities,
            "intent": intent.value,
            "intent_confidence": confidence,
            "parameters": params,
            "semantics": semantics,
            "metrics": {
                "processing_time": round(elapsed, 4),
                "tokens": tokens,
            },
        }
        self.state.last_processed = datetime.now()
        return result

    async def analyze(self, text: str) -> dict[str, Any]:
        return await self.process_text(text, {"mode": "analyze"})

    async def generate(self, request: str, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        import time
        import random
        self.state.start()
        start = time.time()

        intent = self.intent_detection.detect_intent(request)
        params = self.intent_detection.extract_parameters(request)
        if context:
            params.update(context)

        response = self.text_generation.generate_response(intent.value, params)

        elapsed = time.time() - start
        self.metrics.record_processing(elapsed, 1.0, len(request.split()))

        result = {
            "request": request,
            "intent": intent.value,
            "response": response,
            "parameters": params,
            "metrics": {"processing_time": round(elapsed, 4)},
        }
        self.state.last_processed = datetime.now()
        return result
