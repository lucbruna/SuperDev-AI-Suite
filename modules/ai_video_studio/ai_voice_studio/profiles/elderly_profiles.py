"""Elderly profiles — slower, warmer character voices."""
from __future__ import annotations

ELDERLY_PROFILES = [
    {"id": "elderly_man", "name": "Elderly Man", "gender": "elderly", "language": "en-US",
     "edge_voice": "en-US-ChristopherNeural", "gtts_lang": "en", "rate": 0.86, "pitch": 0.88,
     "style": ["elderly", "wise"], "description": "Slow, grandfatherly voice"},
    {"id": "elderly_woman", "name": "Elderly Woman", "gender": "elderly", "language": "en-GB",
     "edge_voice": "en-GB-SoniaNeural", "gtts_lang": "en", "rate": 0.88, "pitch": 0.95,
     "style": ["elderly", "warm"], "description": "Gentle grandmotherly voice"},
    {"id": "elderly_wise", "name": "Wise Sage", "gender": "elderly", "language": "en-US",
     "edge_voice": "en-US-EricNeural", "gtts_lang": "en", "rate": 0.82, "pitch": 0.85,
     "style": ["elderly", "sage"], "description": "Slow contemplative storyteller"},
]
