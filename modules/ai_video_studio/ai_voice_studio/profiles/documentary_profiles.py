"""Documentary profiles — calm, authoritative narration voices."""
from __future__ import annotations

DOCUMENTARY_PROFILES = [
    {"id": "doc_uk_female", "name": "Documentary UK Female", "gender": "female", "language": "en-GB",
     "edge_voice": "en-GB-SoniaNeural", "gtts_lang": "en", "rate": 0.95, "pitch": 1.0,
     "style": ["documentary", "calm"], "description": "BBC-style female narrator"},
    {"id": "doc_uk_male", "name": "Documentary UK Male", "gender": "male", "language": "en-GB",
     "edge_voice": "en-GB-RyanNeural", "gtts_lang": "en", "rate": 0.97, "pitch": 0.96,
     "style": ["documentary", "deep"], "description": "Nature-documentary male voice"},
    {"id": "doc_nature", "name": "Nature Narrator", "gender": "male", "language": "en-US",
     "edge_voice": "en-US-ChristopherNeural", "gtts_lang": "en", "rate": 0.90, "pitch": 0.92,
     "style": ["documentary", "nature"], "description": "Slow, immersive nature narration"},
]
