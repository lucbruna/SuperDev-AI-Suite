"""Prompt parser — turn free text into structured generation directives."""
from __future__ import annotations

import re
from typing import Any


class PromptParser:
    """Extracts subject, style, camera and lighting cues from a prompt."""

    def parse(self, prompt: str) -> dict[str, Any]:
        text = prompt.strip()
        return {
            "raw": text,
            "subject": self._extract_subject(text),
            "style": self._extract_style(text),
            "camera": self._extract_camera(text),
            "lighting": self._extract_lighting(text),
            "negative": self._extract_negative(text),
        }

    def _extract_subject(self, text: str) -> str:
        # Naive heuristic — first noun phrase of the prompt.
        match = re.search(r"\b(the|a|an)\s+([\w\s,]+?)(?:\s*[,.]|\s+(?:with|in|at|on)\b|$)", text, re.IGNORECASE)
        return (match.group(2).strip() if match else text.split(",")[0]).strip()

    def _extract_style(self, text: str) -> str:
        styles = ["anime", "cinematic", "realistic", "fantasy", "pixel art", "watercolor", "3d", "cartoon"]
        for style in styles:
            if re.search(rf"\b{re.escape(style)}\b", text, re.IGNORECASE):
                return style
        return "cinematic"

    def _extract_camera(self, text: str) -> str:
        cams = ["close-up", "wide shot", "drone", "orbit", "handheld", "dolly", "aerial", "low angle"]
        for cam in cams:
            if re.search(rf"\b{re.escape(cam)}\b", text, re.IGNORECASE):
                return cam
        return "wide shot"

    def _extract_lighting(self, text: str) -> str:
        lights = ["golden hour", "neon", "studio", "soft", "dramatic", "backlit", "moody"]
        for light in lights:
            if re.search(rf"\b{re.escape(light)}\b", text, re.IGNORECASE):
                return light
        return "natural"

    def _extract_negative(self, text: str) -> str:
        match = re.search(r"(?:negative|avoid|without)\s*:\s*([^.;]+)", text, re.IGNORECASE)
        return match.group(1).strip() if match else ""
