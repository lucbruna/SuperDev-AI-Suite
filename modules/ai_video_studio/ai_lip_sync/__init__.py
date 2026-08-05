"""AI Lip Sync — phoneme → viseme → facial animation timeline (Volume 4).

Produces real per-frame timelines (JSON) and a mouth-animation MP4, plus
per-feature curves for downstream animators.
"""
from modules.ai_video_studio.ai_lip_sync.lip_sync_engine import LipSyncEngine, get_lip_sync_engine
from modules.ai_video_studio.ai_lip_sync.viseme_mapper import map_phoneme, to_viseme_timeline
from modules.ai_video_studio.ai_lip_sync.phoneme_mapper import map_text_to_phonemes
from modules.ai_video_studio.ai_lip_sync.synchronization_validator import validate_timeline

__all__ = [
    "LipSyncEngine",
    "get_lip_sync_engine",
    "map_phoneme",
    "to_viseme_timeline",
    "map_text_to_phonemes",
    "validate_timeline",
]
