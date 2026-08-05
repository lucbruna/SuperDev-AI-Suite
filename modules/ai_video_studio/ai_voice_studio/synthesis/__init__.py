"""Synthesis engines — chained real TTS for the AI Voice Studio."""
from modules.ai_video_studio.ai_voice_studio.synthesis.tts_engine import TTSEngine, get_tts_engine
from modules.ai_video_studio.ai_voice_studio.synthesis.offline_tts import OfflineTTS
from modules.ai_video_studio.ai_voice_studio.synthesis.emotion_controller import emotion_prosody

__all__ = ["TTSEngine", "get_tts_engine", "OfflineTTS", "emotion_prosody"]
