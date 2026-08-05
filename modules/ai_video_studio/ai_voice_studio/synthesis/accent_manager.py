"""Accent Manager — maps named accents to language/voice settings."""
from __future__ import annotations

ACCENTS: dict[str, dict[str, str]] = {
    "american": {"language": "en-US", "voice": "guy", "description": "General American English"},
    "british": {"language": "en-GB", "voice": "sonia", "description": "Received Pronunciation (UK)"},
    "australian": {"language": "en-AU", "voice": "default", "description": "Australian English"},
    "brazilian": {"language": "pt-BR", "voice": "francisca", "description": "Brazilian Portuguese"},
    "european": {"language": "pt-PT", "voice": "default", "description": "European Portuguese"},
    "spanish": {"language": "es-ES", "voice": "elena", "description": "Castilian Spanish"},
    "mexican": {"language": "es-MX", "voice": "default", "description": "Mexican Spanish"},
    "french": {"language": "fr-FR", "voice": "default", "description": "Metropolitan French"},
    "german": {"language": "de-DE", "voice": "default", "description": "Standard German"},
    "italian": {"language": "it-IT", "voice": "default", "description": "Standard Italian"},
    "japanese": {"language": "ja-JP", "voice": "yuki", "description": "Standard Japanese"},
    "indian": {"language": "en-IN", "voice": "default", "description": "Indian English"},
}


def resolve_accent(accent: str) -> dict[str, str]:
    """Return ``{language, voice}`` for an accent name (defaults to American)."""
    return dict(ACCENTS.get(accent.lower().strip(), ACCENTS["american"]))


def list_accents() -> list[str]:
    return sorted(ACCENTS)
