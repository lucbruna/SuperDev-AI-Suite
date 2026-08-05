"""AI Voice Clone — voice analysis, embeddings and prosodic cloning (Volume 4).

Real DSP analysis (f0, timbre, energy), speaker embeddings, similarity
matching and cloned speech synthesis via prosody transfer + audio
post-processing. Neural conversion can be plugged in later.
"""
from modules.ai_video_studio.ai_voice_clone.clone_engine import CloneEngine, get_clone_engine
from modules.ai_video_studio.ai_voice_clone.voice_analyzer import analyze_file
from modules.ai_video_studio.ai_voice_clone.voice_similarity import similarity_score
from modules.ai_video_studio.ai_voice_clone.speaker_encoder import encode_file

__all__ = [
    "CloneEngine",
    "get_clone_engine",
    "analyze_file",
    "similarity_score",
    "encode_file",
]
