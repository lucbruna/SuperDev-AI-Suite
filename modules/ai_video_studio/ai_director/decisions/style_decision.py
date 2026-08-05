"""Style decision — defines the overall visual style direction."""
from __future__ import annotations

from typing import Any

STYLES = ["documentary", "commercial", "tutorial", "cinematic", "vlog"]


class StyleDecision:
    """Selects the production style."""

    def decide(self, brief: str = "") -> dict[str, Any]:
        lowered = brief.lower()
        if any(word in lowered for word in ("produto", "venda", "comercial")):
            style = "commercial"
        elif any(word in lowered for word in ("tutorial", "como", "guia")):
            style = "tutorial"
        elif any(word in lowered for word in ("história", "filme")):
            style = "cinematic"
        else:
            style = "documentary"
        return {"style": style, "available": STYLES}


_style_decision: StyleDecision | None = None


def get_style_decision() -> StyleDecision:
    global _style_decision
    if _style_decision is None:
        _style_decision = StyleDecision()
    return _style_decision
