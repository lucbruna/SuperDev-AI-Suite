"""AI Dubbing — automatic dubbing pipeline (Volume 4).

Transcribe → translate (Ollama) → synthesize with AI voices → align to the
video timeline → mux. Produces a real dubbed MP4.
"""
from modules.ai_video_studio.ai_dubbing.dubbing_engine import DubbingEngine, get_dubbing_engine
from modules.ai_video_studio.ai_dubbing.multilingual_dubbing import MultilingualDubbing
from modules.ai_video_studio.ai_dubbing.voice_casting import VoiceCasting

__all__ = ["DubbingEngine", "get_dubbing_engine", "MultilingualDubbing", "VoiceCasting"]
