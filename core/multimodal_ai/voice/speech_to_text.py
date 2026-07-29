from typing import Any, Optional, AsyncIterator
import asyncio
import uuid
from datetime import datetime


class SpeechToText:
    def __init__(self) -> None:
        self._languages: dict[str, str] = {
            "en-US": "English (US)",
            "en-GB": "English (UK)",
            "es-ES": "Spanish (Spain)",
            "fr-FR": "French (France)",
            "de-DE": "German (Germany)",
            "zh-CN": "Chinese (Simplified)",
            "ja-JP": "Japanese",
        }
        self._transcriptions: dict[str, dict[str, Any]] = {}

    async def transcribe_audio(self, audio_data: bytes, language: str = "en-US") -> dict[str, Any]:
        await asyncio.sleep(0.01)
        transcription_id = str(uuid.uuid4())
        duration = len(audio_data) / 16000
        text = self._simulate_transcription(audio_data, language)
        result: dict[str, Any] = {
            "transcription_id": transcription_id,
            "text": text,
            "language": language,
            "duration_seconds": round(duration, 2),
            "confidence": round(0.85 + (len(text) % 15) / 100, 2),
            "words": len(text.split()),
            "timestamp": datetime.now().isoformat(),
        }
        self._transcriptions[transcription_id] = result
        return result

    async def transcribe_stream(self, audio_chunks: AsyncIterator[bytes], language: str = "en-US") -> dict[str, Any]:
        full_text_parts: list[str] = []
        async for chunk in audio_chunks:
            await asyncio.sleep(0.005)
            partial = self._simulate_transcription(chunk, language)
            full_text_parts.append(partial)
        combined = " ".join(full_text_parts)
        return {
            "transcription_id": str(uuid.uuid4()),
            "text": combined,
            "language": language,
            "confidence": 0.82,
            "words": len(combined.split()),
            "streaming": True,
        }

    def get_supported_languages(self) -> dict[str, str]:
        return dict(self._languages)

    def get_confidence(self, transcription_id: str) -> Optional[float]:
        entry = self._transcriptions.get(transcription_id)
        return entry["confidence"] if entry else None

    def _simulate_transcription(self, audio_data: bytes, language: str) -> str:
        size = len(audio_data)
        if size > 1000:
            return f"Simulated transcription of {size} bytes of audio data in {language}. This is a demonstration of speech recognition capabilities."
        return "Short audio sample transcribed."
