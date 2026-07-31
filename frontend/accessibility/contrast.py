from __future__ import annotations

from typing import Any

# WCAG 2.x relative luminance / contrast ratio helpers


def _channel(value: int) -> float:
    normalized = value / 255.0
    return (
        normalized / 12.92
        if normalized <= 0.03928
        else ((normalized + 0.055) / 1.055) ** 2.4
    )


def luminance(hex_color: str) -> float:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(ch * 2 for ch in hex_color)
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


class ContrastEngine:
    """Computes WCAG contrast ratios and checks accessibility levels."""

    def ratio(self, fg: str, bg: str) -> float:
        l1 = luminance(fg)
        l2 = luminance(bg)
        lighter, darker = max(l1, l2), min(l1, l2)
        return round((lighter + 0.05) / (darker + 0.05), 2)

    def meets(self, fg: str, bg: str, level: str = "AA", large: bool = False) -> bool:
        ratio = self.ratio(fg, bg)
        if level == "AAA":
            threshold = 3.0 if large else 4.5
        elif level == "AA":
            threshold = 3.0 if large else 4.5
        elif level == "AA_AAA":
            threshold = 4.5 if large else 7.0
        else:
            threshold = 4.5
        return ratio >= threshold

    def best(self, candidates: list[str], bg: str) -> tuple[str, float]:
        best_color, best_ratio = candidates[0], 0.0
        for color in candidates:
            r = self.ratio(color, bg)
            if r > best_ratio:
                best_color, best_ratio = color, r
        return best_color, best_ratio

    def snapshot(self) -> dict[str, Any]:
        return {"method": "WCAG 2.x relative luminance"}
