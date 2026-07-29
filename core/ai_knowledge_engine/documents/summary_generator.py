from __future__ import annotations

import re
from typing import Any


class SummaryGenerator:
    async def generate_summary(self, text: str, max_length: int = 200) -> dict[str, Any]:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        summary_text = " ".join(sentences[:3]) if len(sentences) > 3 else text
        if len(summary_text) > max_length:
            summary_text = summary_text[:max_length].rsplit(" ", 1)[0] + "..."

        return {
            "summary": summary_text,
            "original_length": len(text),
            "summary_length": len(summary_text),
            "compression_ratio": round(len(summary_text) / max(len(text), 1), 4),
            "type": "standard",
        }

    async def generate_executive_summary(self, text: str) -> dict[str, Any]:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        key_sentences = [s for s in sentences if len(s.split()) > 5][:5]
        summary_text = " ".join(key_sentences) if key_sentences else text[:300]

        return {
            "executive_summary": summary_text,
            "key_findings_count": len(key_sentences),
            "type": "executive",
        }

    async def extract_key_points(self, text: str, max_points: int = 5) -> dict[str, Any]:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        scored = sorted(
            [(s, len(s.split())) for s in sentences if len(s.split()) > 3],
            key=lambda x: x[1],
            reverse=True,
        )
        points = [s for s, _ in scored[:max_points]]
        return {
            "key_points": points,
            "count": len(points),
            "type": "key_points",
        }

    async def generate_tldr(self, text: str) -> dict[str, Any]:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        tldr = " ".join(sentences[:1]) if sentences else text
        if len(tldr) > 100:
            tldr = tldr[:100].rsplit(" ", 1)[0] + "..."
        return {
            "tldr": tldr,
            "type": "tldr",
        }

    async def generate_bullet_points(self, text: str) -> dict[str, Any]:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        bullets = [s.strip() for s in sentences if len(s.strip().split()) > 3][:6]
        return {
            "bullet_points": bullets,
            "count": len(bullets),
            "type": "bullet_points",
        }