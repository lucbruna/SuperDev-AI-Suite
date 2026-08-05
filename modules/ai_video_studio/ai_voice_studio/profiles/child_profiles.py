"""Child profiles — playful, higher-pitched character voices."""
from __future__ import annotations

CHILD_PROFILES = [
    {"id": "child_boy", "name": "Child Boy", "gender": "child", "language": "en-US",
     "edge_voice": "en-US-AnaNeural", "gtts_lang": "en", "rate": 1.12, "pitch": 1.30,
     "style": ["child", "playful"], "description": "Young energetic boy's voice"},
    {"id": "child_girl", "name": "Child Girl", "gender": "child", "language": "en-US",
     "edge_voice": "en-US-JennyNeural", "gtts_lang": "en", "rate": 1.10, "pitch": 1.35,
     "style": ["child", "sweet"], "description": "Bright young girl's voice"},
    {"id": "child_teen", "name": "Teenager", "gender": "child", "language": "en-US",
     "edge_voice": "en-US-GuyNeural", "gtts_lang": "en", "rate": 1.06, "pitch": 1.15,
     "style": ["teen", "casual"], "description": "Casual teenage voice"},
]
