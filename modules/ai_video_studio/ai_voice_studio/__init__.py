"""AI Voice Studio — real text-to-speech synthesis core (Volume 4).

Speech synthesis engines (edge-tts → gTTS → pyttsx3), multilingual voices,
expressive/emotion prosody, normalization and narrator profiles. Formant
sound effects are not accepted as spoken narration.
"""
from modules.ai_video_studio.ai_voice_studio.voice_engine import VoiceEngine, get_voice_engine
from modules.ai_video_studio.ai_voice_studio.voice_manager import VoiceManager, get_voice_manager
from modules.ai_video_studio.ai_voice_studio.voice_scheduler import VoiceScheduler, get_voice_scheduler
from modules.ai_video_studio.ai_voice_studio.voice_cache import VoiceCache, get_voice_cache
from modules.ai_video_studio.ai_voice_studio.voice_statistics import VoiceStatistics, get_voice_statistics
from modules.ai_video_studio.ai_voice_studio.voice_models import VoiceSpec, SynthesisRequest, SynthesisResult

__all__ = [
    "VoiceEngine",
    "get_voice_engine",
    "VoiceManager",
    "get_voice_manager",
    "VoiceScheduler",
    "get_voice_scheduler",
    "VoiceCache",
    "get_voice_cache",
    "VoiceStatistics",
    "get_voice_statistics",
    "VoiceSpec",
    "SynthesisRequest",
    "SynthesisResult",
]
