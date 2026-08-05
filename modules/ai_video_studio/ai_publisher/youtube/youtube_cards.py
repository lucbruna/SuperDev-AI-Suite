"""YouTube Cards — info card configurations for videos (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_CARD_TYPES = ("video", "playlist", "channel", "link", "poll")


class YoutubeCards:
    """Compose YouTube info card configurations."""

    def build(self, *, card_type: str = "video", target_id: str = "", teaser_text: str = "", start_seconds: float = 0.0) -> dict:
        """Build one info card descriptor."""
        if card_type not in _CARD_TYPES:
            return {"success": False, "error": f"Invalid card type '{card_type}'"}
        card = {
            "type": card_type,
            "target_id": target_id,
            "teaser_text": teaser_text[:60],
            "start_seconds": max(0.0, float(start_seconds)),
        }
        return {"success": True, "card": card}

    def stats(self) -> dict[str, int]:
        return {"card_types": len(_CARD_TYPES)}


_CARDS: YoutubeCards | None = None


def get_youtube_cards() -> YoutubeCards:
    """Get the module-level singleton cards helper."""
    global _CARDS
    if _CARDS is None:
        _CARDS = YoutubeCards()
    return _CARDS
