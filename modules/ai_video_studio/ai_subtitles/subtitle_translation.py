"""Subtitle Translation — translates cue text with the AI translation engine."""
from __future__ import annotations

import asyncio
from typing import Any

from modules.ai_video_studio.ai_subtitles.subtitle_timeline import SubtitleCue
from modules.ai_video_studio.ai_translation import get_translation_engine


class SubtitleTranslation:
    """Bulk-translates cues while preserving timing."""

    def __init__(self) -> None:
        self.translator = get_translation_engine()

    def translate_cues(self, cues: list[SubtitleCue], target: str, *,
                       source: str | None = None) -> tuple[list[SubtitleCue], dict[str, Any]]:
        """Return (new_cues, report). Sync wrapper for the async engine."""
        try:
            return asyncio.run(self.translate_cues_async(cues, target, source=source))
        except RuntimeError:
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(
                    asyncio.run, self.translate_cues_async(cues, target, source=source)
                ).result()

    async def translate_cues_async(self, cues: list[SubtitleCue], target: str, *,
                                    source: str | None = None) -> tuple[list[SubtitleCue], dict[str, Any]]:
        out: list[SubtitleCue] = []
        engines: set[str] = set()
        for cue in cues:
            result = await self.translator.translate_async(cue.text, target, source=source)
            engines.add(result["engine"])
            out.append(SubtitleCue(cue.index, cue.start, cue.end, result["text"], cue.style))
        return out, {"engine": ", ".join(sorted(engines)), "cues": len(out)}
