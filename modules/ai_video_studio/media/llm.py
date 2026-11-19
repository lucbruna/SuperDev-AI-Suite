"""LLM scene planner — plan scenes through local Ollama.

The planner tries to reach a local Ollama instance and ask it to turn a
prompt into a structured, renderable scene list. When Ollama is not
reachable (or times out), a deterministic fallback planner produces a valid
scene list so generation always works offline.

The ``.env`` may configure ``OLLAMA_BASE_URL`` for Docker (e.g.
``http://host.docker.internal:11434``) which does not resolve on native
Windows/macOS. The client therefore probes several candidate URLs and uses
whichever responds, preferring the configured value.
"""
from __future__ import annotations

import json
import logging
import re
import socket
import urllib.request
from urllib.error import URLError
from typing import Any

logger = logging.getLogger(__name__)


def _configured_base_url() -> str:
    try:
        from modules.ai_video_studio.core.settings import get_settings

        return get_settings().ai.ollama_base_url
    except Exception:  # noqa: BLE001 — settings may be unavailable
        return ""


def _ollama_model() -> str:
    try:
        from modules.ai_video_studio.core.settings import get_settings

        return get_settings().ai.ollama_model
    except Exception:  # noqa: BLE001
        import os

        return os.getenv("OLLAMA_MODEL", "mistral-nemo")


def _candidate_base_urls() -> list[str]:
    """Ordered list of base URLs to try, configured first then localhost."""
    candidates: list[str] = []
    configured = _configured_base_url().strip().rstrip("/")
    if configured:
        candidates.append(configured)
    import os

    env = os.getenv("OLLAMA_BASE_URL", "").strip().rstrip("/")
    if env and env not in candidates:
        candidates.append(env)
    for fallback in ("http://localhost:11434", "http://127.0.0.1:11434"):
        if fallback not in candidates:
            candidates.append(fallback)
    return candidates


def _extract_json(text: str) -> Any:
    """Tolerant JSON extraction from an LLM response."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    for open_ch, close_ch in (("{", "}"), ("[", "]")):
        start = cleaned.find(open_ch)
        if start == -1:
            continue
        depth = 0
        for i in range(start, len(cleaned)):
            if cleaned[i] == open_ch:
                depth += 1
            elif cleaned[i] == close_ch:
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(cleaned[start : i + 1])
                    except json.JSONDecodeError:
                        break
    return None


def generate_text(
    prompt: str,
    *,
    system: str | None = None,
    temperature: float = 0.3,
    timeout: float = 90.0,
    max_tokens: int = 512,
) -> str:
    """Raw local-Ollama completion (public helper used by other subsystems).

    Raises ``RuntimeError`` when no endpoint is reachable so callers can fall
    back to deterministic logic.
    """
    body: dict[str, Any] = {
        "model": _ollama_model(),
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    if system:
        body["system"] = system
    encoded = json.dumps(body).encode("utf-8")
    last_error: Exception | None = None
    for base in _candidate_base_urls():
        url = f"{base}/api/generate"
        try:
            request = urllib.request.Request(
                url,
                data=encoded,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            return str(data.get("response", "")).strip()
        except (URLError, socket.gaierror, OSError, TimeoutError, ValueError) as e:  # noqa: PERF203
            last_error = e
            logger.debug("Ollama unreachable at %s: %s", base, e)
    raise last_error or RuntimeError("No Ollama endpoint reachable")


def _split_prompt_into_scene_beats(prompt: str, num_scenes: int) -> list[str]:
    """Split a brief into contiguous, non-overlapping narrative beats.

    Sentence and clause boundaries are preferred. If the brief contains fewer
    units than requested scenes, contiguous word groups are used rather than
    interleaving words from unrelated parts of the brief.
    """
    count = max(1, int(num_scenes))
    text = re.sub(r"\s+", " ", str(prompt or "")).strip()
    if not text:
        return [f"Parte {index + 1}" for index in range(count)]

    units = [part.strip() for part in re.split(r"(?<=[.!?])\s+|\s*[\n;]+\s*", text) if part.strip()]
    if len(units) < count:
        expanded: list[str] = []
        for unit in units:
            clauses = [part.strip() for part in re.split(r"\s+(?:e então|em seguida|depois|enquanto|mas|porém|porque|quando|e)\\s+|,\\s*", unit, flags=re.IGNORECASE) if part.strip()]
            expanded.extend(clauses if len(clauses) > 1 else [unit])
        units = expanded

    if len(units) < count:
        words = text.split()
        # Balanced contiguous word ranges; never shuffle or omit source words.
        return [
            " ".join(words[(index * len(words)) // count:((index + 1) * len(words)) // count])
            or words[min(index, len(words) - 1)]
            for index in range(count)
        ]

    groups: list[list[str]] = []
    cursor = 0
    for group_index in range(count):
        remaining_groups = count - group_index
        remaining_units = len(units) - cursor
        if remaining_groups == 1:
            groups.append(units[cursor:])
            break
        target_chars = sum(len(item) for item in units[cursor:]) / remaining_groups
        end = cursor
        chars = 0
        max_end = len(units) - (remaining_groups - 1)
        while end < max_end:
            candidate = len(units[end])
            if end > cursor and chars + candidate > target_chars and (target_chars - chars) <= (chars + candidate - target_chars):
                break
            chars += candidate
            end += 1
            if chars >= target_chars:
                break
        end = max(cursor + 1, min(end, max_end))
        groups.append(units[cursor:end])
        cursor = end

    return [" ".join(group).strip() for group in groups]


class ScenePlanner:
    """Plans renderable scenes from a text prompt."""

    SYSTEM_PROMPT = (
        "You are an AI film director and storyboard artist. Convert the video brief "
        "into exactly the requested number of scenes. Return a JSON array only. "
        "Each scene must include name, description, visual_prompt (a detailed standalone "
        "image-generation prompt describing subject, environment, action, composition, "
        "lighting, lens/framing and visual style), negative_prompt, voiceover_text, "
        "shot_type, character_pose (neutral/explain/point), character_expression "
        "(neutral/happy/surprised/concerned), duration, background_colors, particles, circles, rects, lines, "
        "text and camera. Vary shot sizes and angles; do not repeat the same composition. "
        "Never invent facts when the brief is historical or documentary."
    )

    def plan(
        self,
        prompt: str,
        *,
        num_scenes: int = 3,
        duration: float = 10.0,
        timeout: float = 90.0,
    ) -> dict[str, Any]:
        """Return ``{"provider", "model", "ai_generated", "scenes"}``."""
        try:
            payload = self._call_ollama(prompt, num_scenes=num_scenes, duration=duration, timeout=timeout)
            raw = _extract_json(payload)
            scenes = raw if isinstance(raw, list) else raw.get("scenes", []) if isinstance(raw, dict) else []
            if scenes:
                normalized = self._normalize(scenes, num_scenes, duration)
                if len(normalized) < num_scenes:
                    fallback_scenes = self.fallback(
                        prompt, num_scenes=num_scenes, duration=duration,
                    )["scenes"]
                    normalized.extend(fallback_scenes[len(normalized):num_scenes])
                return {"provider": "ollama", "model": _ollama_model(), "ai_generated": True, "scenes": normalized}
            logger.warning("Ollama returned no scenes — falling back to deterministic planner")
        except Exception as e:  # noqa: BLE001 — any failure falls back
            logger.warning("Ollama planning failed (%s) — using deterministic planner", e)
        return self.fallback(prompt, num_scenes=num_scenes, duration=duration)

    # ── Ollama call ───────────────────────────────────────────────
    def _call_ollama(self, prompt: str, *, num_scenes: int, duration: float, timeout: float) -> str:
        return generate_text(
            f"Video brief: {prompt}\n\n"
            f"Produce exactly {num_scenes} scenes summing to about {duration}s "
            f"of video. Now write the JSON array.\n",
            system=self.SYSTEM_PROMPT,
            temperature=0.7,
            timeout=timeout,
            max_tokens=min(8192, max(1024, num_scenes * 256)),
        )

    # ── Normalisation ─────────────────────────────────────────────
    def _normalize(self, raw: list[Any], num_scenes: int, duration: float) -> list[dict[str, Any]]:
        per_scene = duration / max(num_scenes, 1)
        scenes: list[dict[str, Any]] = []
        for i, item in enumerate(raw[:num_scenes]):
            if not isinstance(item, dict):
                continue
            try:
                s_duration = float(item.get("duration") or per_scene)
            except (TypeError, ValueError):
                s_duration = per_scene
            scenes.append(
                {
                    "index": i,
                    "name": str(item.get("name") or f"Scene {i + 1}")[:255],
                    "description": str(item.get("description") or "")[:1000],
                    "visual_prompt": str(item.get("visual_prompt") or item.get("image_prompt") or item.get("description") or item.get("name") or "")[:2000],
                    "negative_prompt": str(item.get("negative_prompt") or "")[:1000],
                    "voiceover_text": str(item.get("voiceover_text") or item.get("narration") or "")[:2000],
                    "shot_type": str(item.get("shot_type") or "medium")[:32],
                    "character_pose": str(item.get("character_pose") or "")[:24],
                    "character_expression": str(item.get("character_expression") or "")[:24],
                    "duration": max(0.5, s_duration),
                    "background_colors": self._coerce_colors(item.get("background_colors")),
                    "particles": self._coerce_list(item.get("particles")),
                    "circles": self._coerce_list(item.get("circles")),
                    "rects": self._coerce_list(item.get("rects")),
                    "lines": self._coerce_list(item.get("lines")),
                    "text": item.get("text"),
                    "camera": item.get("camera") if isinstance(item.get("camera"), dict) else None,
                    "palette": self._coerce_colors(item.get("palette")),
                }
            )
        return scenes

    @staticmethod
    def _coerce_colors(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [c for c in value if isinstance(c, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", c)]

    @staticmethod
    def _coerce_list(value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        return [v for v in value if isinstance(v, dict)]

    # ── Deterministic fallback ────────────────────────────────────
    def fallback(self, prompt: str, *, num_scenes: int = 3, duration: float = 10.0) -> dict[str, Any]:
        """Deterministic scene plan usable with no LLM available."""
        beats = _split_prompt_into_scene_beats(prompt, num_scenes)
        per_scene = duration / max(num_scenes, 1)
        palette = ["#1a1a2e", "#0f3460", "#533483", "#e94560", "#16213e"]
        scenes: list[dict[str, Any]] = []
        for i, chunk in enumerate(beats):
            if not chunk:
                chunk = f"Parte {i + 1}"
            scenes.append(
                {
                    "index": i,
                    "name": f"Scene {i + 1}",
                    "description": chunk[:1000],
                    "visual_prompt": f"{prompt}. Scene focus: {chunk}. Clear subject, detailed environment, cinematic composition, purposeful camera framing.",
                    "negative_prompt": "blurry, low quality, distorted anatomy, unreadable text, watermark, logo",
                    "voiceover_text": chunk[:1000],
                    "shot_type": ("establishing", "wide", "medium", "close_up", "detail")[i % 5],
                    "character_pose": ("explain", "point", "neutral")[i % 3],
                    "character_expression": ("neutral", "happy", "surprised")[i % 3],
                    "duration": per_scene,
                    "background_colors": [palette[i % len(palette)], palette[(i + 1) % len(palette)]],
                    "particles": [
                        {"x": (k * 137) % 1280, "y": -10.0, "vx": -0.3, "vy": 1.2 + (k % 3) * 0.3,
                         "radius": 2, "color": "#FFFFFF", "alpha": 0.7}
                        for k in range(10)
                    ],
                    "circles": [{"x": 640 + i * 30, "y": 240, "radius": 60 + i * 10, "color": "#FFFFFF22", "dx": 0.2, "dy": 0.0}],
                    "rects": [],
                    "lines": [],
                    "text": {"content": chunk, "size": 44, "color": "#FFFFFF"},
                    "camera": {"dx": -0.4, "dy": 0.0, "zoom": 1.0, "roll": 0.0},
                    "palette": palette,
                }
            )
        return {"provider": None, "model": None, "ai_generated": False, "scenes": scenes}


_scene_planner: ScenePlanner | None = None


def get_scene_planner() -> ScenePlanner:
    global _scene_planner
    if _scene_planner is None:
        _scene_planner = ScenePlanner()
    return _scene_planner
