"""AI Studio services — AI Director / AI Screenwriter / AI Storyboard.

This layer implements the "real AI" phase of the video studio (blueprint
Volume 2). It reuses the platform's existing LLM provider system
(``ai.llm`` + ``backend.services.settings_service``) instead of duplicating
provider logic, mirroring the provider-resolution pattern already used by
``backend/api/v1/llm.py`` so the studio honors providers saved in the
Settings UI and env-var fallbacks.

Three roles compose a generation request:

1. ``AIDirector`` — breaks a text prompt into a shot list: scene types,
   durations, transitions, pacing and a one-line description per scene.
2. ``AIScreenwriter`` — writes the narration/script and the voiceover text
   for every scene produced by the director.
3. ``AIStoryboard`` — turns each scene into a concrete visual prompt and
   background color for the render engine.

``AIStudioService`` orchestrates the three roles and also exposes a
deterministic fallback planner that is used when no LLM provider is
configured, so the module keeps working without API keys.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from modules.ai_video_studio.core.exceptions import AIError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Vocabulary shared by prompts and fallbacks
# ---------------------------------------------------------------------------

VALID_SCENE_TYPES = (
    "intro", "content", "transition", "outro",
    "title_card", "b_roll", "highlight", "credits",
)
VALID_TRANSITIONS = ("cut", "fade", "dissolve", "wipe", "slide", "zoom", "none")

STYLE_PALETTES = {
    "cinematic": ["#1a1a2e", "#16213e", "#0f3460", "#533483", "#e94560"],
    "corporate": ["#2c3e50", "#34495e", "#7f8c8d", "#95a5a6", "#bdc3c7"],
    "vibrant": ["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#3498db"],
    "pastel": ["#ffeaa7", "#fab1a0", "#81ecec", "#74b9ff", "#dfe6e9"],
    "dark": ["#0d0d0d", "#1a1a1a", "#2d2d2d", "#404040", "#595959"],
    "nature": ["#27ae60", "#2ecc71", "#1abc9c", "#16a085", "#2c3e50"],
    "warm": ["#d35400", "#e67e22", "#f39c12", "#e74c3c", "#c0392b"],
}

SYSTEM_PROMPT_TAIL = (
    "\n\nReturn ONLY a valid JSON payload. Do not include markdown fences, "
    "explanations, or any text outside the JSON object."
)


def _default_text_color(style: str) -> str:
    return "#333333" if style == "pastel" else "#FFFFFF"


def _coerce_scene_type(value: Any) -> str:
    if value in VALID_SCENE_TYPES:
        return value
    return "content"


def _coerce_transition(value: Any, fallback: str = "cut") -> str:
    if value in VALID_TRANSITIONS:
        return value
    return fallback


# ---------------------------------------------------------------------------
# LLM client — reuses the backend provider stack
# ---------------------------------------------------------------------------


class LLMClient:
    """Thin wrapper over the platform LLM factory + provider instances.

    Resolution order (same as ``backend/api/v1/llm.py``):

    1. Explicit provider/model passed by the caller.
    2. First provider in ``PROVIDER_ENV_MAP`` that has a key (DB-saved
       setting first, then environment variable).
    """

    _factory: Any = None

    @classmethod
    def _get_factory(cls) -> Any:
        if cls._factory is not None:
            return cls._factory
        try:
            from ai.llm import LLMFactory, PROVIDER_CLASSES

            factory = LLMFactory()
            factory.register_all(PROVIDER_CLASSES)
            cls._factory = factory
            logger.info("LLMFactory initialized (%d provider types)", factory.type_count)
        except Exception as e:  # noqa: BLE001 — ai.llm may be missing in isolation
            logger.warning("LLM factory unavailable: %s", e)
            cls._factory = None
        return cls._factory

    @staticmethod
    async def _db_provider_config(db: AsyncSession | None, provider_name: str) -> dict[str, Any]:
        if db is None:
            return {}
        try:
            from backend.services.settings_service import get_runtime_provider_config

            return await get_runtime_provider_config(db, provider_name)
        except Exception as e:  # noqa: BLE001 — settings table may be missing
            logger.debug("DB provider config unavailable for %s: %s", provider_name, e)
            return {}

    @classmethod
    async def resolve(
        cls,
        provider: str | None = None,
        model: str | None = None,
        db: AsyncSession | None = None,
    ) -> tuple[str, str]:
        """Return ``(provider_name, model)`` for the best available provider."""
        if provider:
            return provider, model or ""

        from ai.llm.providers import PROVIDER_DEFAULT_MODELS, PROVIDER_ENV_MAP

        for name in PROVIDER_ENV_MAP:
            saved = await cls._db_provider_config(db, name)
            api_key_var = PROVIDER_ENV_MAP[name].get("api_key", "")
            if saved.get("api_key") or _env(api_key_var):
                return name, model or saved.get("model") or PROVIDER_DEFAULT_MODELS.get(name, "")

        return "", ""

    @classmethod
    async def _create_instance(
        cls,
        provider_name: str,
        model: str | None = None,
        db: AsyncSession | None = None,
    ) -> Any | None:
        factory = cls._get_factory()
        if not factory:
            return None
        try:
            from ai.llm.providers import PROVIDER_DEFAULT_MODELS

            resolved_model = model or PROVIDER_DEFAULT_MODELS.get(provider_name, "")
            kwargs: dict[str, Any] = {"model": resolved_model}

            saved = await cls._db_provider_config(db, provider_name)
            if saved.get("api_key"):
                kwargs["api_key"] = saved["api_key"]
            if saved.get("base_url"):
                kwargs["base_url"] = saved["base_url"]
            if saved.get("model"):
                kwargs["model"] = saved["model"]

            try:
                return factory.create(provider_name, **kwargs)
            except TypeError:
                # Some providers (e.g. MockProvider) do not accept a `model`
                # kwarg; retry without it before giving up.
                kwargs.pop("model", None)
                return factory.create(provider_name, **kwargs)
        except Exception as e:  # noqa: BLE001
            logger.error("Failed to create provider %s: %s", provider_name, e)
            return None

    @classmethod
    async def generate(
        cls,
        prompt: str,
        *,
        system: str,
        provider: str | None = None,
        model: str | None = None,
        db: AsyncSession | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> dict[str, Any]:
        """Run a completion and return ``{"content", "provider", "model", "usage"}``.

        Raises ``AIError`` when no provider is configured or the call fails.
        """
        provider_name, resolved_model = await cls.resolve(provider, model, db)
        if not provider_name:
            raise AIError(
                "No LLM provider configured. Set API keys in environment variables or Settings.",
                context={"error": "no_provider"},
            )

        instance = await cls._create_instance(provider_name, resolved_model, db)
        if instance is None:
            raise AIError(
                f"Provider '{provider_name}' could not be initialized.",
                context={"error": "provider_init_failed", "provider": provider_name},
            )

        try:
            result = await instance.generate(
                prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                system=system,
            )
        except Exception as e:  # noqa: BLE001 — surface as structured AI error
            logger.error("LLM generate failed for %s: %s", provider_name, e)
            raise AIError(f"LLM call to '{provider_name}' failed: {e}") from e

        if not result.get("success", True) or not result.get("content"):
            raise AIError(
                result.get("error") or f"Provider '{provider_name}' returned an empty response.",
                context={"error": "empty_response", "provider": provider_name},
            )

        return {
            "content": str(result["content"]),
            "provider": provider_name,
            "model": instance.model(),
            "usage": {
                "prompt_tokens": result.get("tokens_prompt", 0),
                "completion_tokens": result.get("tokens_completion", 0),
                "cost_usd": result.get("cost_usd", 0.0),
            },
        }


def _env(var_name: str) -> str:
    import os

    return os.getenv(var_name, "")


# ---------------------------------------------------------------------------
# JSON parsing helpers
# ---------------------------------------------------------------------------


def extract_json(text: str) -> Any:
    """Parse a JSON payload out of an LLM response.

    Tolerates markdown fences, trailing prose and unbalanced extra braces.
    """
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

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


# ---------------------------------------------------------------------------
# AI Director
# ---------------------------------------------------------------------------


class AIDirector:
    """Plans the shot list: scene types, durations, transitions, pacing."""

    SYSTEM_PROMPT = (
        "You are an expert AI film director. Given a video brief, you produce "
        "a structured shot list. Split the brief into logical scenes with "
        "varied scene types (intro, content, transition, outro, title_card, "
        "b_roll, highlight, credits), sensible per-scene durations, and "
        "appropriate transitions (cut, fade, dissolve, wipe, slide, zoom)."
        + SYSTEM_PROMPT_TAIL
    )

    async def plan(
        self,
        prompt: str,
        *,
        num_scenes: int,
        duration: float,
        style: str,
        language: str,
        provider: str | None = None,
        model: str | None = None,
        db: AsyncSession | None = None,
    ) -> list[dict[str, Any]]:
        user_prompt = (
            f"Video brief: {prompt}\n\n"
            f"Target: {num_scenes} scenes, total duration {duration:.1f}s, "
            f"visual style '{style}', narration language '{language}'.\n\n"
            'Respond with a JSON array of objects, each with exactly: '
            '"name", "description", "scene_type", "duration_seconds", '
            '"transition_in", "transition_out", "transition_duration". '
            "Sum of duration_seconds should be close to the total duration."
        )
        result = await LLMClient.generate(
            user_prompt,
            system=self.SYSTEM_PROMPT,
            provider=provider,
            model=model,
            db=db,
            temperature=0.7,
            max_tokens=2048,
        )
        payload = extract_json(result["content"])
        raw_scenes = payload if isinstance(payload, list) else payload.get("scenes", []) if isinstance(payload, dict) else []
        return self._normalize(raw_scenes, num_scenes, duration, style)

    def _normalize(
        self,
        raw: list[Any],
        num_scenes: int,
        duration: float,
        style: str,
    ) -> list[dict[str, Any]]:
        scenes: list[dict[str, Any]] = []
        per_scene = duration / max(num_scenes, 1)
        for i, item in enumerate(raw[:num_scenes]):
            if not isinstance(item, dict):
                continue
            scene_type = _coerce_scene_type(item.get("scene_type"))
            try:
                s_duration = float(item.get("duration_seconds") or per_scene)
            except (TypeError, ValueError):
                s_duration = per_scene
            s_duration = max(1.0, min(s_duration, duration))

            first = i == 0
            scenes.append(
                {
                    "index": i,
                    "name": str(item.get("name") or f"Scene {i + 1}")[:255],
                    "description": str(item.get("description") or "")[:1000] or None,
                    "scene_type": scene_type,
                    "duration": s_duration,
                    "transition_in": "none" if first else _coerce_transition(item.get("transition_in")),
                    "transition_out": _coerce_transition(item.get("transition_out")),
                    "transition_duration": max(0.0, float(item.get("transition_duration") or 0.5)),
                    "background_color": None,
                    "text_color": _default_text_color(style),
                    "font_size": 48 if first else 36,
                }
            )
        # Ensure we return exactly num_scenes entries even when the LLM
        # returned fewer; pad with fallback-shaped scenes.
        for i in range(len(scenes), num_scenes):
            scenes.append(
                {
                    "index": i,
                    "name": f"Scene {i + 1}",
                    "description": None,
                    "scene_type": "content",
                    "duration": duration / num_scenes,
                    "transition_in": "cut" if i > 0 else "none",
                    "transition_out": "cut",
                    "transition_duration": 0.5,
                    "background_color": None,
                    "text_color": _default_text_color(style),
                    "font_size": 36,
                }
            )
        return scenes


# ---------------------------------------------------------------------------
# AI Screenwriter
# ---------------------------------------------------------------------------


class AIScreenwriter:
    """Writes the narration/script and voiceover text per scene."""

    SYSTEM_PROMPT = (
        "You are an expert AI screenwriter. For each scene of a video you "
        "write (a) 'script' — the on-screen narration as it would appear as "
        "text/closed caption, and (b) 'voiceover_text' — natural spoken "
        "voiceover for that scene. Write in the requested language, keep "
        "each scene concise and punchy." + SYSTEM_PROMPT_TAIL
    )

    async def write(
        self,
        prompt: str,
        scenes: list[dict[str, Any]],
        *,
        language: str,
        provider: str | None = None,
        model: str | None = None,
        db: AsyncSession | None = None,
    ) -> list[dict[str, Any]]:
        brief = "\n".join(
            f"Scene {s['index']} ({s['scene_type']}): {s['name']} — {s['description'] or 'no description'}"
            for s in scenes
        )
        user_prompt = (
            f"Video brief: {prompt}\n\n"
            f"Language: {language}\n\n"
            f"Scenes to write for:\n{brief}\n\n"
            'Respond with a JSON array of objects, each with exactly: '
            '"index" (matching the scene index), "script", "voiceover_text".'
        )
        result = await LLMClient.generate(
            user_prompt,
            system=self.SYSTEM_PROMPT,
            provider=provider,
            model=model,
            db=db,
            temperature=0.8,
            max_tokens=2048,
        )
        payload = extract_json(result["content"])
        raw = payload if isinstance(payload, list) else payload.get("scenes", []) if isinstance(payload, dict) else []
        return self._merge(raw, scenes)

    def _merge(self, raw: list[Any], scenes: list[dict[str, Any]]) -> list[dict[str, Any]]:
        by_index: dict[int, dict[str, Any]] = {}
        for item in raw:
            if not isinstance(item, dict):
                continue
            idx_raw = item.get("index")
            if idx_raw is None:
                continue
            try:
                idx = int(idx_raw)
            except (TypeError, ValueError):
                continue
            by_index[idx] = item

        for s in scenes:
            extra = by_index.get(s["index"], {})
            s["script"] = str(extra.get("script") or s.get("name") or "")[:5000] or None
            s["voiceover_text"] = str(extra.get("voiceover_text") or "")[:5000] or None
        return scenes


# ---------------------------------------------------------------------------
# AI Storyboard
# ---------------------------------------------------------------------------


class AIStoryboard:
    """Turns each scene into a visual prompt + background color."""

    SYSTEM_PROMPT = (
        "You are an expert AI storyboard artist and visual director. For each "
        "scene you write (a) 'visual_prompt' — a vivid, camera-ready text "
        "prompt describing the imagery, framing, lighting and mood, and (b) "
        "'background_color' — a single hex color (e.g. '#1a1a2e') matching "
        "the scene mood and the requested style." + SYSTEM_PROMPT_TAIL
    )

    async def generate(
        self,
        prompt: str,
        scenes: list[dict[str, Any]],
        *,
        style: str,
        provider: str | None = None,
        model: str | None = None,
        db: AsyncSession | None = None,
    ) -> list[dict[str, Any]]:
        brief = "\n".join(
            f"Scene {s['index']} ({s['scene_type']}): {s['name']} — {s['description'] or 'no description'} | script: {s.get('script') or '—'}"
            for s in scenes
        )
        user_prompt = (
            f"Video brief: {prompt}\n\n"
            f"Visual style: {style}\n\n"
            f"Scenes to visualize:\n{brief}\n\n"
            'Respond with a JSON array of objects, each with exactly: '
            '"index", "visual_prompt", "background_color".'
        )
        result = await LLMClient.generate(
            user_prompt,
            system=self.SYSTEM_PROMPT,
            provider=provider,
            model=model,
            db=db,
            temperature=0.7,
            max_tokens=2048,
        )
        payload = extract_json(result["content"])
        raw = payload if isinstance(payload, list) else payload.get("scenes", []) if isinstance(payload, dict) else []
        return self._merge(raw, scenes, style)

    def _merge(
        self,
        raw: list[Any],
        scenes: list[dict[str, Any]],
        style: str,
    ) -> list[dict[str, Any]]:
        palette = STYLE_PALETTES.get(style, STYLE_PALETTES["cinematic"])
        by_index: dict[int, dict[str, Any]] = {}
        for item in raw:
            if not isinstance(item, dict):
                continue
            idx_raw = item.get("index")
            if idx_raw is None:
                continue
            try:
                idx = int(idx_raw)
            except (TypeError, ValueError):
                continue
            by_index[idx] = item

        for s in scenes:
            extra = by_index.get(s["index"], {})
            visual = str(extra.get("visual_prompt") or s.get("description") or s.get("name") or "")
            color = str(extra.get("background_color") or palette[s["index"] % len(palette)])
            if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
                color = palette[s["index"] % len(palette)]
            s["visual_prompt"] = visual[:2000] or None
            s["background_color"] = color
        return scenes


# ---------------------------------------------------------------------------
# Orchestration + deterministic fallback
# ---------------------------------------------------------------------------


class AIStudioService:
    """End-to-end AI generation: director → screenwriter → storyboard.

    When no LLM provider is available, falls back to a deterministic planner
    so generation endpoints and pipelines remain functional offline.
    """

    def __init__(self) -> None:
        self.director = AIDirector()
        self.screenwriter = AIScreenwriter()
        self.storyboard = AIStoryboard()

    @classmethod
    async def has_provider(cls, db: AsyncSession | None = None) -> bool:
        provider_name, _ = await LLMClient.resolve(db=db)
        return bool(provider_name)

    def fallback_plan(
        self,
        prompt: str,
        *,
        num_scenes: int,
        duration: float,
        style: str,
        language: str,
    ) -> list[dict[str, Any]]:
        """Deterministic scene plan used when no provider is configured."""
        words = prompt.split() or ["Scene"]
        words_per_scene = max(1, len(words) // num_scenes)
        scene_duration = duration / max(num_scenes, 1)
        palette = STYLE_PALETTES.get(style, STYLE_PALETTES["cinematic"])

        scenes: list[dict[str, Any]] = []
        for i in range(num_scenes):
            start_word = i * words_per_scene
            scene_words = words[start_word : min(start_word + words_per_scene, len(words))]
            scene_text = " ".join(scene_words) if scene_words else f"Scene {i + 1}"
            first = i == 0
            scenes.append(
                {
                    "index": i,
                    "name": f"Scene {i + 1}",
                    "description": scene_text[:1000],
                    "scene_type": "intro" if first else ("outro" if i == num_scenes - 1 and num_scenes > 2 else "content"),
                    "duration": scene_duration,
                    "script": scene_text,
                    "voiceover_text": scene_text,
                    "visual_prompt": scene_text,
                    "background_color": palette[i % len(palette)],
                    "text_color": _default_text_color(style),
                    "font_size": 48 if first else 36,
                    "transition_in": "none" if first else "fade",
                    "transition_out": "fade",
                    "transition_duration": 0.5,
                }
            )
        return scenes

    async def generate_project(
        self,
        prompt: str,
        *,
        num_scenes: int = 3,
        duration: float = 10.0,
        style: str = "cinematic",
        language: str = "en",
        provider: str | None = None,
        model: str | None = None,
        db: AsyncSession | None = None,
    ) -> dict[str, Any]:
        """Generate a full project plan (scenes with script, voiceover, visuals)."""
        if not await self.has_provider(db):
            scenes = self.fallback_plan(
                prompt, num_scenes=num_scenes, duration=duration,
                style=style, language=language,
            )
            return {"provider": None, "model": None, "ai_generated": False, "scenes": scenes}

        scenes = await self.director.plan(
            prompt, num_scenes=num_scenes, duration=duration,
            style=style, language=language, provider=provider, model=model, db=db,
        )
        scenes = await self.screenwriter.write(
            prompt, scenes, language=language, provider=provider, model=model, db=db,
        )
        scenes = await self.storyboard.generate(
            prompt, scenes, style=style, provider=provider, model=model, db=db,
        )

        resolved_provider, resolved_model = await LLMClient.resolve(provider, model, db)
        return {
            "provider": resolved_provider or None,
            "model": resolved_model or None,
            "ai_generated": True,
            "scenes": scenes,
        }

    async def expand_scene(
        self,
        prompt: str,
        scene: dict[str, Any],
        *,
        style: str = "cinematic",
        language: str = "en",
        provider: str | None = None,
        model: str | None = None,
        db: AsyncSession | None = None,
    ) -> dict[str, Any]:
        """Deepen a single scene: richer script, voiceover and visual prompt."""
        if not await self.has_provider(db):
            return {"provider": None, "model": None, "ai_generated": False, "scene": {**scene}}

        scenes = [scene]
        scenes = await self.screenwriter.write(
            prompt, scenes, language=language, provider=provider, model=model, db=db,
        )
        scenes = await self.storyboard.generate(
            prompt, scenes, style=style, provider=provider, model=model, db=db,
        )
        resolved_provider, resolved_model = await LLMClient.resolve(provider, model, db)
        return {
            "provider": resolved_provider or None,
            "model": resolved_model or None,
            "ai_generated": True,
            "scene": scenes[0],
        }
