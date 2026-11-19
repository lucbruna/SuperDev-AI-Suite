"""Optional Stable Diffusion WebUI API adapter for scene image creation/editing.

This is a real image-model integration, unlike the procedural style renderer.
It targets an explicitly configured local AUTOMATIC1111-compatible API and
never silently pretends procedural output is AI-generated.
"""
from __future__ import annotations

import base64
import json
import math
import os
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse
from typing import Any

from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename


def _api_base_url() -> str:
    value = os.getenv("DARKSTUDIO_IMAGE_API_URL", "http://127.0.0.1:7860").strip().rstrip("/")
    parsed = urlparse(value)
    local_hosts = {"127.0.0.1", "localhost", "host.docker.internal"}
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("DARKSTUDIO_IMAGE_API_URL must be a valid local or trusted HTTPS image API URL")
    if parsed.scheme == "http" and parsed.hostname not in local_hosts:
        raise ValueError("Plain HTTP image APIs are only allowed on localhost or host.docker.internal")
    if parsed.query or parsed.fragment:
        raise ValueError("DARKSTUDIO_IMAGE_API_URL cannot contain a query string or fragment")
    return value


def fit_image_dimensions(width: int, height: int, max_edge: int | None = None) -> tuple[int, int]:
    """Fit dimensions to a diffusion-friendly maximum edge while preserving aspect ratio.

    The default 768px cap is conservative for local GPUs with 6GB VRAM.
    Override it with DARKSTUDIO_IMAGE_MAX_EDGE for stronger hardware.
    """
    if max_edge is None:
        try:
            max_edge = int(os.getenv("DARKSTUDIO_IMAGE_MAX_EDGE", "768"))
        except ValueError as exc:
            raise ValueError("DARKSTUDIO_IMAGE_MAX_EDGE must be an integer") from exc
    if width < 1 or height < 1 or max_edge < 64 or max_edge > 2048:
        raise ValueError("image dimensions must be positive and max_edge between 64 and 2048")
    scale = min(1.0, max_edge / max(width, height))
    fitted_width = max(64, int(width * scale) // 8 * 8)
    fitted_height = max(64, int(height * scale) // 8 * 8)
    return fitted_width, fitted_height


def _post_json(url: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Image model API request failed: {exc}") from exc
    if not isinstance(result, dict):
        raise RuntimeError("Image model API returned an invalid response")
    return result


def _decode_image(result: dict[str, Any], prefix: str) -> dict[str, Any]:
    images = result.get("images")
    if not isinstance(images, list) or not images or not isinstance(images[0], str):
        raise RuntimeError("Image model API returned no image")
    encoded = images[0].split(",", 1)[-1]
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise RuntimeError("Image model API returned invalid base64 image data") from exc
    if not raw:
        raise RuntimeError("Image model API returned an empty image")
    from io import BytesIO
    from PIL import Image, UnidentifiedImageError

    try:
        with Image.open(BytesIO(raw)) as decoded:
            if decoded.format != "PNG":
                raise RuntimeError("Image model API must return PNG images")
            decoded.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise RuntimeError("Image model API returned a corrupt or unsupported image") from exc
    output = unique_filename(get_subsystem_dir("images"), prefix, "png")
    output.write_bytes(raw)
    return {
        "image_path": str(output),
        "image_bytes": len(raw),
        "provider": "automatic1111_compatible",
        "status": "generated",
    }


def generate_scene_image(
    prompt: str,
    *,
    negative_prompt: str = "",
    width: int = 768,
    height: int = 768,
    steps: int = 20,
    cfg_scale: float = 7.0,
    seed: int = -1,
    timeout: float = 240.0,
) -> dict[str, Any]:
    if not prompt.strip():
        raise ValueError("scene image prompt cannot be empty")
    if width < 64 or height < 64 or width > 2048 or height > 2048:
        raise ValueError("image dimensions must be between 64 and 2048")
    if steps < 1 or steps > 60:
        raise ValueError("image steps must be between 1 and 60")
    if not math.isfinite(cfg_scale) or cfg_scale < 1 or cfg_scale > 20:
        raise ValueError("cfg_scale must be between 1 and 20")
    if timeout < 1 or timeout > 900:
        raise ValueError("image timeout must be between 1 and 900 seconds")
    payload = {
        "prompt": prompt[:4000],
        "negative_prompt": negative_prompt[:2000],
        "width": width,
        "height": height,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "seed": int(seed),
        "batch_size": 1,
        "n_iter": 1,
        "save_images": False,
    }
    result = _post_json(f"{_api_base_url()}/sdapi/v1/txt2img", payload, timeout)
    output = _decode_image(result, "darkstudio_scene")
    output.update({"generation_info": result.get("info"), "operation": "text_to_image", "seed": int(seed)})
    return output


def edit_image(
    source_path: str | Path,
    prompt: str,
    *,
    negative_prompt: str = "",
    denoising_strength: float = 0.45,
    steps: int = 20,
    cfg_scale: float = 7.0,
    seed: int = -1,
    timeout: float = 240.0,
) -> dict[str, Any]:
    source = Path(source_path).resolve()
    if not source.is_file() or source.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise ValueError("source image must be an existing PNG, JPG or WebP file")
    if not prompt.strip():
        raise ValueError("image edit prompt cannot be empty")
    if not math.isfinite(denoising_strength) or not 0.05 <= denoising_strength <= 0.95:
        raise ValueError("denoising_strength must be between 0.05 and 0.95")
    if steps < 1 or steps > 60:
        raise ValueError("image steps must be between 1 and 60")
    if not math.isfinite(cfg_scale) or cfg_scale < 1 or cfg_scale > 20:
        raise ValueError("cfg_scale must be between 1 and 20")
    if timeout < 1 or timeout > 900:
        raise ValueError("image timeout must be between 1 and 900 seconds")
    encoded = base64.b64encode(source.read_bytes()).decode("ascii")
    payload = {
        "init_images": [encoded],
        "prompt": prompt[:4000],
        "negative_prompt": negative_prompt[:2000],
        "denoising_strength": denoising_strength,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "seed": int(seed),
        "batch_size": 1,
        "n_iter": 1,
        "save_images": False,
    }
    result = _post_json(f"{_api_base_url()}/sdapi/v1/img2img", payload, timeout)
    output = _decode_image(result, "darkstudio_edit")
    output.update({"operation": "image_to_image", "source_path": str(source), "seed": int(seed)})
    return output
