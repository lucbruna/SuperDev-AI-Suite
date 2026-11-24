"""ComfyUI still-image provider with explicit per-character reference inputs.

This provider is intentionally separate from ComfyUIVideoProvider: it submits
an API-format image workflow and accepts image outputs only. Each approved
character reference is uploaded independently and mapped to a configured
LoadImage node. Workflow-specific node IDs must be supplied by the operator.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError


class ComfyUIImageProvider:
    """Generate a still image from a ComfyUI API workflow."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        workflow_path: str | Path | None = None,
        mapping: dict[str, Any] | None = None,
        timeout: float = 600.0,
        poll_interval: float = 1.0,
    ) -> None:
        self.base_url = (base_url or os.getenv("DARKSTUDIO_COMFYUI_URL", "")).rstrip("/")
        configured = workflow_path or os.getenv("DARKSTUDIO_COMFYUI_IMAGE_WORKFLOW")
        self.workflow_path = Path(configured).expanduser() if configured else None
        self.mapping = mapping if mapping is not None else self._mapping_from_env()
        self.timeout = min(1800.0, max(5.0, float(timeout)))
        self.poll_interval = min(10.0, max(0.2, float(poll_interval)))

    @staticmethod
    def _mapping_from_env() -> dict[str, Any]:
        raw = os.getenv("DARKSTUDIO_COMFYUI_IMAGE_MAPPING", "").strip()
        if not raw:
            return {}
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValidationError("DARKSTUDIO_COMFYUI_IMAGE_MAPPING must be valid JSON") from exc
        if not isinstance(value, dict):
            raise ValidationError("ComfyUI image mapping must be a JSON object")
        return value

    def is_configured(self) -> bool:
        return bool(self.base_url and self.workflow_path and self.workflow_path.is_file() and self.mapping)

    def generate(
        self,
        *,
        prompt: str,
        references_by_character: dict[str, str | Path],
        output_path: str | Path,
        negative_prompt: str = "",
    ) -> dict[str, Any]:
        if not self.base_url:
            raise ValidationError("Set DARKSTUDIO_COMFYUI_URL to enable ComfyUI image generation")
        if not self.workflow_path or not self.workflow_path.is_file():
            raise ValidationError("Set DARKSTUDIO_COMFYUI_IMAGE_WORKFLOW to an API-format image workflow JSON")
        if not isinstance(self.mapping, dict) or not self.mapping:
            raise ValidationError("Set DARKSTUDIO_COMFYUI_IMAGE_MAPPING with explicit workflow node/input IDs")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValidationError("ComfyUI image prompt cannot be empty")
        if not isinstance(references_by_character, dict) or not references_by_character:
            raise ValidationError("At least one approved character reference is required")

        workflow = json.loads(self.workflow_path.read_text(encoding="utf-8"))
        if not isinstance(workflow, dict) or not workflow:
            raise ValidationError("ComfyUI image workflow must be a non-empty API-format node object")

        character_mapping = self.mapping.get("characters")
        if not isinstance(character_mapping, dict) or set(character_mapping) != set(references_by_character):
            raise ValidationError("ComfyUI image character mapping must exactly match supplied character references")

        uploaded: dict[str, dict[str, Any]] = {}
        for character_id, raw_path in references_by_character.items():
            if not isinstance(character_id, str) or not character_id.strip():
                raise ValidationError("Character IDs must be non-empty strings")
            source = Path(raw_path).expanduser()
            if not source.is_file() or source.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
                raise ValidationError(f"Approved reference for '{character_id}' must be an existing PNG, JPG or WebP")
            if source.stat().st_size <= 0 or source.stat().st_size > 12 * 1024 * 1024:
                raise ValidationError(f"Approved reference for '{character_id}' is empty or exceeds 12 MiB")
            uploaded[character_id] = self._upload_image(source)

        self._apply_mapping(workflow, uploaded, prompt.strip(), negative_prompt.strip())
        submitted = self._json_request(
            "POST", "/prompt",
            {"prompt": workflow, "client_id": f"darkstudio-image-{uuid.uuid4().hex}"},
        )
        prompt_id = str(submitted.get("prompt_id") or "")
        if not prompt_id:
            raise RuntimeError("ComfyUI did not return a prompt_id for the image workflow")

        history = self._wait_for_history(prompt_id)
        image_entry = self._find_image_output(history)
        target = Path(output_path)
        if target.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            raise ValidationError("ComfyUI image output path must use PNG, JPG or WebP")
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._download_output(image_entry, target)
            self._validate_image(target)
        except Exception:
            target.unlink(missing_ok=True)
            raise

        return {
            "provider": "comfyui_image_workflow",
            "prompt_id": prompt_id,
            "output_path": str(target),
            "character_ids": sorted(references_by_character),
            "reference_count": len(uploaded),
            "workflow": str(self.workflow_path),
            "image_metadata": image_entry,
        }

    def _apply_mapping(
        self,
        workflow: dict[str, Any],
        uploaded_by_character: dict[str, dict[str, Any]],
        prompt: str,
        negative_prompt: str,
    ) -> None:
        prompt_node = self.mapping.get("prompt")
        negative_node = self.mapping.get("negative_prompt")
        if not isinstance(prompt_node, dict):
            raise ValidationError("ComfyUI image mapping requires a prompt node")
        reserved = {self._target(prompt_node)}
        if negative_node is not None:
            if not isinstance(negative_node, dict):
                raise ValidationError("negative_prompt mapping must be an object")
            reserved.add(self._target(negative_node))
        if any(not all(target) for target in reserved):
            raise ValidationError("Prompt mappings require explicit node_id and input")

        occupied: set[tuple[str, str]] = set()
        for character_id in sorted(uploaded_by_character):
            spec = self.mapping["characters"].get(character_id)
            uploaded = uploaded_by_character[character_id]
            if not isinstance(spec, dict) or not isinstance(uploaded, dict):
                raise ValidationError(f"Invalid image mapping for character '{character_id}'")
            target = self._target(spec)
            if not all(target) or target in occupied or target in reserved:
                raise ValidationError("Each character reference must map to a distinct input separate from prompt inputs")
            name = str(uploaded.get("name") or "").strip()
            if not name:
                raise ValidationError(f"ComfyUI upload returned no image name for '{character_id}'")
            subfolder = str(uploaded.get("subfolder") or "").strip("/")
            self._set_input(workflow, spec, f"{subfolder}/{name}" if subfolder else name)
            occupied.add(target)

        self._set_input(workflow, prompt_node, prompt)
        if negative_node is not None and negative_prompt:
            self._set_input(workflow, negative_node, negative_prompt)

    @staticmethod
    def _target(spec: dict[str, Any]) -> tuple[str, str]:
        return str(spec.get("node_id") or ""), str(spec.get("input") or "")

    @staticmethod
    def _set_input(workflow: dict[str, Any], spec: dict[str, Any], value: str) -> None:
        node_id, input_name = ComfyUIImageProvider._target(spec)
        node = workflow.get(node_id)
        if not node_id or not input_name or not isinstance(node, dict) or not isinstance(node.get("inputs"), dict):
            raise ValidationError("ComfyUI image workflow node/input mapping was not found")
        if input_name not in node["inputs"]:
            raise ValidationError(f"Input '{input_name}' not found on ComfyUI image node '{node_id}'")
        node["inputs"][input_name] = value

    def _upload_image(self, image: Path) -> dict[str, Any]:
        boundary = f"----DarkStudioImage{uuid.uuid4().hex}"
        body = bytearray()
        body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n".encode())
        body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{image.name}\"\r\n".encode())
        body.extend(b"Content-Type: application/octet-stream\r\n\r\n")
        body.extend(image.read_bytes() + b"\r\n")
        body.extend(f"--{boundary}--\r\n".encode())
        request = urllib.request.Request(
            f"{self.base_url}/upload/image", data=bytes(body), method="POST",
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        return self._read_json(request)

    def _json_request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            f"{self.base_url}{path}", data=data, method=method,
            headers={"Content-Type": "application/json"} if data else {},
        )
        return self._read_json(request)

    @staticmethod
    def _read_json(request: urllib.request.Request) -> dict[str, Any]:
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"ComfyUI image request failed: {exc}") from exc
        if not isinstance(result, dict):
            raise RuntimeError("ComfyUI image API returned an invalid JSON object")
        return result

    def _wait_for_history(self, prompt_id: str) -> dict[str, Any]:
        deadline = time.monotonic() + self.timeout
        while time.monotonic() < deadline:
            history = self._json_request("GET", f"/history/{urllib.parse.quote(prompt_id)}")
            record = history.get(prompt_id)
            if isinstance(record, dict):
                status = record.get("status") or {}
                if status.get("status_str") == "error":
                    raise RuntimeError(f"ComfyUI image workflow failed: {status.get('messages')}")
                if record.get("outputs"):
                    return record
            time.sleep(self.poll_interval)
        raise TimeoutError(f"ComfyUI image workflow {prompt_id} timed out after {self.timeout:g}s")

    @staticmethod
    def _find_image_output(history: dict[str, Any]) -> dict[str, Any]:
        outputs = history.get("outputs") or {}
        for node_id, node in outputs.items():
            if not isinstance(node, dict):
                continue
            for item in node.get("images") or []:
                if isinstance(item, dict) and str(item.get("filename") or "").lower().endswith(
                    (".png", ".jpg", ".jpeg", ".webp")
                ):
                    return {**item, "node_id": str(node_id), "media_key": "images"}
        raise RuntimeError("ComfyUI image workflow completed without a still-image output")

    def _download_output(self, item: dict[str, Any], target: Path) -> None:
        query = urllib.parse.urlencode({
            "filename": str(item.get("filename") or ""),
            "subfolder": str(item.get("subfolder") or ""),
            "type": str(item.get("type") or "output"),
        })
        request = urllib.request.Request(f"{self.base_url}/view?{query}", method="GET")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response, target.open("wb") as output:
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            target.unlink(missing_ok=True)
            raise RuntimeError(f"Could not download ComfyUI still image: {exc}") from exc

    @staticmethod
    def _validate_image(path: Path) -> None:
        from PIL import Image, UnidentifiedImageError

        try:
            with Image.open(path) as image:
                if image.format not in {"PNG", "JPEG", "WEBP"}:
                    raise RuntimeError("ComfyUI returned an unsupported still-image format")
                image.verify()
        except (UnidentifiedImageError, OSError) as exc:
            raise RuntimeError("ComfyUI returned a corrupt or unsupported still image") from exc
