import pytest
from ..speech_to_text import SpeechToText
from ..text_to_speech import TextToSpeech
from ..voice_recognition import VoiceRecognizer
from ..speaker_identification import SpeakerIdentifier
from ..voice_engine import VoiceEngine


class TestSpeechToText:
    def setup_method(self) -> None:
        self.stt = SpeechToText()

    @pytest.mark.asyncio
    async def test_transcribe_audio(self) -> None:
        result = await self.stt.transcribe_audio(b"test audio data " * 100)
        assert "transcription_id" in result
        assert result["confidence"] > 0

    @pytest.mark.asyncio
    async def test_transcribe_audio_short(self) -> None:
        result = await self.stt.transcribe_audio(b"hi", "en-US")
        assert result["text"] is not None

    @pytest.mark.asyncio
    async def test_supported_languages(self) -> None:
        langs = self.stt.get_supported_languages()
        assert "en-US" in langs
        assert "fr-FR" in langs


class TestTextToSpeech:
    def setup_method(self) -> None:
        self.tts = TextToSpeech()

    @pytest.mark.asyncio
    async def test_synthesize_speech(self) -> None:
        result = await self.tts.synthesize_speech("Hello world")
        assert "output_id" in result
        assert result["duration_seconds"] > 0

    def test_set_voice(self) -> None:
        assert self.tts.set_voice("en-US-Neural2-A")
        assert not self.tts.set_voice("nonexistent")

    def test_set_speed(self) -> None:
        self.tts.set_speed(2.0)
        assert self.tts._current_speed == 2.0
        self.tts.set_speed(10.0)
        assert self.tts._current_speed == 4.0

    def test_get_available_voices(self) -> None:
        voices = self.tts.get_available_voices()
        assert len(voices) >= 4


class TestVoiceRecognizer:
    def setup_method(self) -> None:
        self.recognizer = VoiceRecognizer()

    @pytest.mark.asyncio
    async def test_recognize_command_dashboard(self) -> None:
        result = await self.recognizer.recognize_command("open dashboard please")
        assert result["command"] == "open_dashboard"

    @pytest.mark.asyncio
    async def test_recognize_command_unknown(self) -> None:
        result = await self.recognizer.recognize_command("xyzzy")
        assert result["command"] == "unknown"

    @pytest.mark.asyncio
    async def test_extract_command_params(self) -> None:
        params = await self.recognizer.extract_command_params("schedule on 15/03/2026 at 14:30")
        assert "date" in params
        assert "time" in params


class TestSpeakerIdentifier:
    def setup_method(self) -> None:
        self.si = SpeakerIdentifier()

    @pytest.mark.asyncio
    async def test_enroll_and_identify(self) -> None:
        enroll = await self.si.enroll_speaker("Alice", b"sample_audio_data_123")
        assert enroll["status"] == "enrolled"
        identify = await self.si.identify_speaker(b"sample_audio_data_123")
        assert identify["identified"]
        assert identify["speaker_name"] == "Alice"

    @pytest.mark.asyncio
    async def test_verify_speaker(self) -> None:
        enroll = await self.si.enroll_speaker("Bob", b"bob_voice_sample")
        verify = await self.si.verify_speaker(enroll["speaker_id"], b"bob_voice_sample")
        assert verify["verified"]

    @pytest.mark.asyncio
    async def test_list_enrolled_speakers(self) -> None:
        await self.si.enroll_speaker("Charlie", b"charlie_audio")
        speakers = self.si.list_enrolled_speakers()
        assert len(speakers) >= 1


class TestVoiceEngine:
    @pytest.mark.asyncio
    async def test_process_audio(self) -> None:
        engine = VoiceEngine()
        result = await engine.process_audio(b"audio data " * 50)
        assert "transcription" in result
        assert "recognition" in result

    @pytest.mark.asyncio
    async def test_transcribe(self) -> None:
        engine = VoiceEngine()
        result = await engine.transcribe(b"hello world " * 20, "en-US")
        assert result["confidence"] > 0

    @pytest.mark.asyncio
    async def test_synthesize(self) -> None:
        engine = VoiceEngine()
        result = await engine.synthesize("Test synthesis")
        assert result["duration_seconds"] > 0

    @pytest.mark.asyncio
    async def test_engine_state_and_metrics(self) -> None:
        engine = VoiceEngine()
        assert engine.state.status == "idle"
        await engine.process_audio(b"test data")
        assert engine.metrics.audios_processed >= 1

    @pytest.mark.asyncio
    async def test_engine_config_custom(self) -> None:
        engine = VoiceEngine()
        result = await engine.process_audio(b"data " * 30)
        assert result["speaker"]["identified"] is False
