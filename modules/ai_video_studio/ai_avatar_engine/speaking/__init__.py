"""Speaking Avatar — narrated talking-presenter video (avatar × voice × lip-sync).

Bridges the AI Avatar & Digital Human Engine (Volume 6) with the AI Voice
Studio (Volume 4) and the AI Lip Sync (Volume 4): synthesize narration,
time the viseme timeline to the audio, drive the avatar's facial rig per
frame and render + mux a real video file.
"""
from modules.ai_video_studio.ai_avatar_engine.speaking.speaking_engine import (
    SpeakingAvatarEngine,
    compose_facial,
    get_speaking_engine,
)

__all__ = ["SpeakingAvatarEngine", "compose_facial", "get_speaking_engine"]
