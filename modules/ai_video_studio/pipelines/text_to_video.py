"""Text-to-Video pipeline — generates video scenes from a text prompt.

This pipeline:
1. Plans scenes from the prompt (splits into logical segments)
2. Generates placeholder visuals per scene (solid color + text overlay via FFmpeg)
3. Concatenates scenes into a single video
4. Generates thumbnail
"""
from __future__ import annotations
import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Any

from modules.ai_video_studio.pipelines import BasePipeline
from modules.ai_video_studio.render_engine import RenderEngine

logger = logging.getLogger(__name__)

# Scene style color palettes
STYLE_PALETTES = {
    "cinematic": ["#1a1a2e", "#16213e", "#0f3460", "#533483", "#e94560"],
    "corporate": ["#2c3e50", "#34495e", "#7f8c8d", "#95a5a6", "#bdc3c7"],
    "vibrant": ["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#3498db"],
    "pastel": ["#ffeaa7", "#fab1a0", "#81ecec", "#74b9ff", "#dfe6e9"],
    "dark": ["#0d0d0d", "#1a1a1a", "#2d2d2d", "#404040", "#595959"],
    "nature": ["#27ae60", "#2ecc71", "#1abc9c", "#16a085", "#2c3e50"],
    "warm": ["#d35400", "#e67e22", "#f39c12", "#e74c3c", "#c0392b"],
}


def _plan_scenes(prompt: str, num_scenes: int, duration: float, style: str) -> list[dict]:
    """Split a text prompt into scene segments with visual parameters."""
    words = prompt.split()
    if not words:
        words = ["Scene"]

    scenes = []
    words_per_scene = max(1, len(words) // num_scenes)
    scene_duration = duration / num_scenes
    palette = STYLE_PALETTES.get(style, STYLE_PALETTES["cinematic"])

    for i in range(num_scenes):
        start_word = i * words_per_scene
        end_word = min(start_word + words_per_scene, len(words))
        scene_words = words[start_word:end_word]
        scene_text = " ".join(scene_words) if scene_words else f"Scene {i + 1}"

        bg_color = palette[i % len(palette)]
        text_color = "#FFFFFF" if style != "pastel" else "#333333"

        scenes.append({
            "index": i,
            "text": scene_text,
            "duration": scene_duration,
            "background_color": bg_color,
            "text_color": text_color,
            "font_size": 48 if i == 0 else 36,
            "transition": "fade" if i > 0 else "none",
        })

    return scenes


class TextToVideoPipeline(BasePipeline):
    """Generate a video from a text prompt by creating text-over-color scenes."""

    name = "text_to_video"

    async def plan(self, **kwargs: Any) -> list[str]:
        return [
            "plan_scenes",
            "generate_scene_videos",
            "concatenate_scenes",
            "generate_thumbnail",
        ]

    async def execute_step(self, step_name: str, plan: list[str], **kwargs: Any) -> Any:
        prompt = kwargs.get("prompt", "Hello World")
        duration = kwargs.get("duration", 10.0)
        resolution = kwargs.get("resolution", "1920x1080")
        num_scenes = kwargs.get("num_scenes", 3)
        style = kwargs.get("style", "cinematic")

        if step_name == "plan_scenes":
            scenes = await self._plan_scenes_ai(prompt, num_scenes, duration, style)
            self._scenes = scenes
            self._resolution = resolution
            self._style = style
            return scenes

        if step_name == "generate_scene_videos":
            engine = RenderEngine()
            scene_paths = []
            for scene in self._scenes:
                path = await self._render_scene(engine, scene, resolution)
                scene_paths.append(path)
            self._scene_paths = scene_paths
            return scene_paths

        if step_name == "concatenate_scenes":
            engine = RenderEngine()
            output_path = str(
                Path(tempfile.gettempdir()) / f"avs_pipeline_{self.pipeline_id}.mp4"
            )
            result = await engine.concat_videos(self._scene_paths, output_path)
            self.result.output_path = output_path
            self.result.duration = duration
            return result

        if step_name == "generate_thumbnail":
            if self.result.output_path:
                engine = RenderEngine()
                thumb_path = str(
                    Path(tempfile.gettempdir()) / f"avs_thumb_{self.pipeline_id}.jpg"
                )
                await engine.generate_thumbnail(self.result.output_path, thumb_path)
                self.result.metadata["thumbnail"] = thumb_path
                return thumb_path
            return None

        raise ValueError(f"Unknown step: {step_name}")

    async def _plan_scenes_ai(self, prompt: str, num_scenes: int, duration: float, style: str) -> list[dict]:
        """Plan scenes via the AI studio (director) with deterministic fallback.

        Uses env-var provider resolution (no DB session available inside the
        pipeline). When no provider is configured the deterministic planner is
        used, keeping the pipeline fully functional offline.
        """
        try:
            from modules.ai_video_studio.services.ai_studio import AIStudioService

            service = AIStudioService()
            if await service.has_provider(db=None):
                result = await service.generate_project(
                    prompt, num_scenes=num_scenes, duration=duration, style=style,
                )
                ai_scenes = result["scenes"]
                # Adapt rich AI scenes to the renderer's expected shape.
                return [
                    {
                        "index": s["index"],
                        "text": s.get("script") or s.get("description") or s.get("name") or f"Scene {s['index'] + 1}",
                        "duration": s["duration"],
                        "background_color": s.get("background_color") or "#1a1a2e",
                        "text_color": s.get("text_color") or "#FFFFFF",
                        "font_size": s.get("font_size", 36),
                        "transition": "fade" if s["index"] > 0 else "none",
                    }
                    for s in ai_scenes
                ]
            logger.info("No LLM provider configured; using deterministic scene planner")
        except Exception as e:  # noqa: BLE001 — never let AI planning break the pipeline
            logger.warning("AI scene planning failed, falling back to deterministic: %s", e)
        return _plan_scenes(prompt, num_scenes, duration, style)

    async def _render_scene(self, engine: RenderEngine, scene: dict, resolution: str) -> str:
        """Render a single scene: solid background + text overlay via FFmpeg."""
        w, h = resolution.split("x")
        output = str(
            Path(tempfile.gettempdir()) / f"avs_scene_{self.pipeline_id}_{scene['index']}.mp4"
        )
        bg = scene["background_color"]
        text = scene["text"][:60]
        tc = scene["text_color"]
        fs = scene["font_size"]

        # Generate a video with colored background and text overlay
        drawtext_filter = (
            f"drawtext=text='{text}':"
            f"fontcolor={tc}:fontsize={fs}:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:"
            f"borderw=2:bordercolor=black"
        )

        cmd = [
            engine.ffmpeg, "-y",
            "-f", "lavfi", "-i",
            f"color=c={bg}:s={resolution}:d={scene['duration']}:r=30",
            "-f", "lavfi", "-i",
            "anullsrc=r=44100:cl=stereo",
            "-vf", drawtext_filter,
            "-c:v", "libx264", "-crf", "23", "-preset", "fast",
            "-c:a", "aac", "-b:a", "128k",
            "-t", str(scene["duration"]),
            "-shortest",
            "-pix_fmt", "yuv420p",
            output,
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"Scene render failed: {stderr.decode()[:500]}")
        return output
