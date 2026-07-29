"""
Multimodal Configuration - All multimodal AI engine settings.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TextConfig:
    enabled: bool = True
    max_length: int = 4096
    language: str = "en"
    enable_sentiment: bool = True
    enable_entities: bool = True
    enable_summarization: bool = True


@dataclass
class VoiceConfig:
    enabled: bool = True
    stt_language: str = "en-US"
    tts_voice: str = "default"
    tts_speed: float = 1.0
    enable_recording: bool = True
    enable_transcription: bool = True
    max_duration_seconds: int = 300
    sample_rate: int = 16000
    enable_speaker_diarization: bool = False


@dataclass
class VisionConfig:
    enabled: bool = True
    enable_object_detection: bool = True
    enable_face_recognition: bool = False
    enable_ocr: bool = True
    enable_scene_analysis: bool = True
    max_image_size_mb: float = 10.0
    supported_formats: List[str] = field(default_factory=lambda: ["jpg", "jpeg", "png", "webp", "bmp", "tiff"])
    resolution_width: int = 1920
    resolution_height: int = 1080


@dataclass
class VideoConfig:
    enabled: bool = True
    max_duration_seconds: int = 600
    enable_frame_extraction: bool = True
    frame_extraction_rate: int = 1
    enable_motion_detection: bool = True
    enable_scene_detection: bool = True
    supported_formats: List[str] = field(default_factory=lambda: ["mp4", "avi", "mov", "mkv", "webm"])
    max_file_size_mb: float = 500.0


@dataclass
class DocumentConfig:
    enabled: bool = True
    enable_parsing: bool = True
    enable_summarization: bool = True
    enable_qa: bool = True
    max_pages: int = 100
    supported_formats: List[str] = field(default_factory=lambda: ["pdf", "docx", "doc", "txt", "rtf", "odt", "html", "md", "csv", "xlsx", "pptx"])
    max_file_size_mb: float = 50.0


@dataclass
class SensorConfig:
    enabled: bool = True
    enable_temperature: bool = True
    enable_humidity: bool = True
    enable_pressure: bool = True
    enable_motion: bool = True
    enable_light: bool = True
    enable_audio_level: bool = True
    enable_proximity: bool = True
    polling_interval_seconds: int = 5
    data_retention_hours: int = 24


@dataclass
class ConversationConfig:
    max_context_messages: int = 100
    max_session_duration_minutes: int = 120
    enable_context_linking: bool = True
    enable_cross_modality_reference: bool = True
    idle_timeout_minutes: int = 30
    auto_save: bool = True


@dataclass
class TranslationConfig:
    enabled: bool = True
    source_language: str = "auto"
    target_language: str = "en"
    enable_auto_detect: bool = True
    supported_languages: List[str] = field(default_factory=lambda: ["en", "pt", "es", "fr", "de", "it", "ja", "zh", "ko", "ru", "ar"])
    enable_formal_mode: bool = False


@dataclass
class MultimodalConfig:
    engine_name: str = "MultimodalAIEngine"
    engine_version: str = "1.0.0"
    environment: str = "production"
    log_level: str = "INFO"
    enable_telemetry: bool = True
    default_timeout_seconds: int = 30
    max_concurrent_sessions: int = 100
    text: TextConfig = field(default_factory=TextConfig)
    voice: VoiceConfig = field(default_factory=VoiceConfig)
    vision: VisionConfig = field(default_factory=VisionConfig)
    video: VideoConfig = field(default_factory=VideoConfig)
    documents: DocumentConfig = field(default_factory=DocumentConfig)
    sensors: SensorConfig = field(default_factory=SensorConfig)
    conversation: ConversationConfig = field(default_factory=ConversationConfig)
    translation: TranslationConfig = field(default_factory=TranslationConfig)
    _extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MultimodalConfig":
        config = cls()
        for key, value in data.items():
            if hasattr(config, key) and not key.startswith("_"):
                if isinstance(value, dict) and key in cls.__dataclass_fields__:
                    sub = getattr(config, key)
                    if hasattr(sub, "__dataclass_fields__"):
                        for sk, sv in value.items():
                            if hasattr(sub, sk):
                                setattr(sub, sk, sv)
                        continue
                setattr(config, key, value)
            else:
                config._extra[key] = value
        return config

    @classmethod
    def from_json(cls, path: str) -> "MultimodalConfig":
        if not os.path.exists(path):
            return cls()
        with open(path) as f:
            return cls.from_dict(json.load(f))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

    def validate(self) -> List[str]:
        errors = []
        if self.text.max_length < 1:
            errors.append("text.max_length must be positive")
        if self.voice.sample_rate not in (8000, 16000, 22050, 44100, 48000):
            errors.append("voice.sample_rate must be a standard rate (8000, 16000, 22050, 44100, 48000)")
        if self.vision.max_image_size_mb <= 0:
            errors.append("vision.max_image_size_mb must be positive")
        if self.video.max_duration_seconds <= 0:
            errors.append("video.max_duration_seconds must be positive")
        if self.documents.max_pages < 1:
            errors.append("documents.max_pages must be at least 1")
        if self.sensors.polling_interval_seconds < 1:
            errors.append("sensors.polling_interval_seconds must be at least 1")
        if self.conversation.max_context_messages < 1:
            errors.append("conversation.max_context_messages must be at least 1")
        return errors
