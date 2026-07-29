from typing import Any, Optional, AsyncIterator
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class VoiceEngineConfig:
    default_language: str = "en-US"
    default_voice: str = "en-US-Neural2-A"
    speech_speed: float = 1.0
    enable_speaker_identification: bool = True
    streaming_chunk_size: int = 4096


@dataclass
class VoiceEngineState:
    status: str = "idle"
    started_at: Optional[datetime] = None
    last_processed: Optional[datetime] = None
    error_count: int = 0
    active_streams: int = 0

    def start(self) -> None:
        self.status = "running"
        self.started_at = datetime.now()

    def stop(self) -> None:
        self.status = "stopped"


@dataclass
class VoiceEngineMetrics:
    audios_processed: int = 0
    total_processing_time: float = 0.0
    average_confidence: float = 0.0
    transcriptions_count: int = 0
    syntheses_count: int = 0
    speakers_identified: int = 0

    def record_processing(self, time: float, confidence: float) -> None:
        self.audios_processed += 1
        self.total_processing_time += time
        self.average_confidence = (
            (self.average_confidence * (self.audios_processed - 1) + confidence)
            / self.audios_processed
        )


class VoiceEngine:
    def __init__(self, config: Optional[VoiceEngineConfig] = None) -> None:
        self.config = config or VoiceEngineConfig()
        self.state = VoiceEngineState()
        self.metrics = VoiceEngineMetrics()
        from .speech_to_text import SpeechToText
        from .text_to_speech import TextToSpeech
        from .voice_recognition import VoiceRecognizer
        from .speaker_identification import SpeakerIdentifier
        self.speech_to_text = SpeechToText()
        self.text_to_speech = TextToSpeech()
        self.voice_recognition = VoiceRecognizer()
        self.speaker_identification = SpeakerIdentifier()

    async def process_audio(self, audio_data: bytes, options: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        import time
        self.state.start()
        start = time.time()

        transcription = await self.speech_to_text.transcribe_audio(
            audio_data,
            options.get("language", self.config.default_language) if options else self.config.default_language,
        )

        recognition = await self.voice_recognition.recognize_command(transcription["text"])

        speaker_result: dict[str, Any] = {}
        if self.config.enable_speaker_identification:
            speaker_result = await self.speaker_identification.identify_speaker(audio_data)

        elapsed = time.time() - start
        self.metrics.record_processing(elapsed, transcription["confidence"])
        if speaker_result.get("identified"):
            self.metrics.speakers_identified += 1
        self.metrics.transcriptions_count += 1

        result = {
            "transcription": transcription,
            "recognition": recognition,
            "speaker": speaker_result,
            "metrics": {
                "processing_time": round(elapsed, 4),
                "audio_size_bytes": len(audio_data),
            },
        }
        self.state.last_processed = datetime.now()
        return result

    async def transcribe(self, audio_data: bytes, language: Optional[str] = None) -> dict[str, Any]:
        import time
        start = time.time()
        result = await self.speech_to_text.transcribe_audio(
            audio_data, language or self.config.default_language
        )
        elapsed = time.time() - start
        self.metrics.record_processing(elapsed, result["confidence"])
        self.metrics.transcriptions_count += 1
        return result

    async def synthesize(self, text: str, voice_id: Optional[str] = None) -> dict[str, Any]:
        import time
        start = time.time()
        result = await self.text_to_speech.synthesize_speech(text, voice_id)
        elapsed = time.time() - start
        self.metrics.record_processing(elapsed, 1.0)
        self.metrics.syntheses_count += 1
        return result

    async def recognize_speaker(self, audio_data: bytes) -> dict[str, Any]:
        import time
        start = time.time()
        result = await self.speaker_identification.identify_speaker(audio_data)
        elapsed = time.time() - start
        self.metrics.record_processing(elapsed, result["confidence"])
        if result.get("identified"):
            self.metrics.speakers_identified += 1
        return result
