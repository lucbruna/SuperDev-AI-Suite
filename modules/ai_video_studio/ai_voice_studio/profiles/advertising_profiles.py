"""Advertising profiles — energetic, persuasive promo voices."""
from __future__ import annotations

ADVERTISING_PROFILES = [
    {"id": "ad_energetic", "name": "Ad Energetic", "gender": "female", "language": "en-US",
     "edge_voice": "en-US-AnaNeural", "gtts_lang": "en", "rate": 1.22, "pitch": 1.12,
     "style": ["advertising", "energetic"], "description": "High-energy promo voice"},
    {"id": "ad_deep", "name": "Ad Deep", "gender": "male", "language": "en-US",
     "edge_voice": "en-US-ChristopherNeural", "gtts_lang": "en", "rate": 0.96, "pitch": 0.90,
     "style": ["advertising", "movie"], "description": "Movie-trailer promo voice"},
    {"id": "ad_smooth", "name": "Ad Smooth", "gender": "male", "language": "en-US",
     "edge_voice": "en-US-GuyNeural", "gtts_lang": "en", "rate": 1.05, "pitch": 0.97,
     "style": ["advertising", "smooth"], "description": "Silky sales voice"},
    {"id": "ad_pt", "name": "Promo PT", "gender": "male", "language": "pt-BR",
     "edge_voice": "pt-BR-AntonioNeural", "gtts_lang": "pt", "rate": 1.10, "pitch": 1.0,
     "style": ["advertising", "portuguese"], "description": "Brazilian promo announcer"},
]
