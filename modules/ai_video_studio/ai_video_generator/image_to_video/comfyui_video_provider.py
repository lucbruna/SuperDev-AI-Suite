"""Optional ComfyUI image-to-video adapter.

The user supplies an API-format workflow exported by ComfyUI and an explicit
node/input mapping. This deliberately avoids assuming a particular Wan node
graph or third-party custom-node schema.
"""
from __future__ import annotations

import json
import os
import time
import uuid
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError


class ComfyUIVideoProvider:
    """Submit an image-to-video workflow to a configured ComfyUI server."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        workflow_path: str | Path | None = None,
        mapping: dict[str, Any] | None = None,
        timeout: float = 900.0,
        poll_interval: float = 2.0,
    ) -> None:
        self.base_url = (base_url or os.getenv("DARKSTUDIO_COMFYUI_URL", "")).rstrip("/")
        configured_workflow = workflow_path or os.getenv("DARKSTUDIO_COMFYUI_WORKFLOW")
        self.workflow_path = Path(configured_workflow).expanduser() if configured_workflow else None
        raw_mapping = mapping
        if raw_mapping is None:
            raw_mapping = self._load_mapping_env()
        self.mapping = raw_mapping or {}
        self.timeout = max(5.0, float(timeout))
        self.poll_interval = max(0.2, float(poll_interval))

    @staticmethod
    def _load_mapping_env() -> dict[str, Any]:
        raw = os.getenv("DARKSTUDIO_COMFYUI_MAPPING", "").strip()
        if not raw:
            return {}
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValidationError("DARKSTUDIO_COMFYUI_MAPPING must be valid JSON") from exc
        if not isinstance(value, dict):
            raise ValidationError("ComfyUI node mapping must be a JSON object")
        return value

    def is_configured(self) -> bool:
        return bool(self.base_url and self.workflow_path and self.workflow_path.is_file())

    def generate(
        self,
        *,
        image_path: str | Path,
        prompt: str,
        negative_prompt: str = "",
        output_path: str | Path,
    ) -> dict[str, Any]:
        if not self.base_url:
            raise ValidationError("Set DARKSTUDIO_COMFYUI_URL to enable ComfyUI video generation")
        if not self.workflow_path or not self.workflow_path.is_file():
            raise ValidationError("Set DARKSTUDIO_COMFYUI_WORKFLOW to an API-format workflow JSON file")
        if not self.mapping:
            raise ValidationError("Set DARKSTUDIO_COMFYUI_MAPPING with the workflow node/input IDs")
        source = Path(image_path)
        if not source.is_file():
            raise ValidationError("ComfyUI image-to-video requires an existing source image", field="image_path")

        workflow = json.loads(self.workflow_path.read_text(encoding="utf-8"))
        if not isinstance(workflow, dict) or not workflow:
            raise ValidationError("ComfyUI workflow must be a non-empty API-format node object")
        uploaded = self._upload_image(source)
        self._apply_mapping(workflow, uploaded, prompt, negative_prompt)
        prompt_result = self._json_request(
            "POST", "/prompt", {"prompt": workflow, "client_id": f"darkstudio-{uuid.uuid4().hex}"}
        )
        prompt_id = str(prompt_result.get("prompt_id") or "")
        if not prompt_id:
            raise RuntimeError("ComfyUI did not return a prompt_id")

        history = self._wait_for_history(prompt_id)
        video_entry = self._find_video_output(history)
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        self._download_output(video_entry, target)
        with target.open("rb") as stream:
            signature = stream.read(12)
        if len(signature) < 8 or signature[4:8] != b"ftyp":
            target.unlink(missing_ok=True)
            raise RuntimeError("ComfyUI workflow output is not a valid MP4 file")

        return {
            "provider": "comfyui_workflow",
            "prompt_id": prompt_id,
            "output_path": str(target),
            "source_image": str(source),
            "workflow": str(self.workflow_path),
            "video_metadata": video_entry,
        }

    def _apply_mapping(
        self, workflow: dict[str, Any], uploaded: dict[str, Any],
        prompt: str, negative_prompt: str,
    ) -> None:
        image_node = self.mapping.get("image")
        prompt_node = self.mapping.get("prompt")
        if not isinstance(image_node, dict) or not isinstance(prompt_node, dict):
            raise ValidationError("Mapping requires image and prompt node definitions")
        self._set_node_input(workflow, image_node, str(uploaded.get("name") or ""))
        self._set_node_input(workflow, prompt_node, prompt)
        negative_node = self.mapping.get("negative_prompt")
        if negative_node and negative_prompt:
            if not isinstance(negative_node, dict):
                raise ValidationError("negative_prompt mapping must be an object")
            self._set_node_input(workflow, negative_node, negative_prompt)

    @staticmethod
    def _set_node_input(workflow: dict[str, Any], spec: dict[str, Any], value: str) -> None:
        node_id = str(spec.get("node_id") or "")
        input_name = str(spec.get("input") or "")
        if not node_id or not input_name:
            raise ValidationError("Each ComfyUI mapping needs node_id and input")
        node = workflow.get(node_id)
        if not isinstance(node, dict) or not isinstance(node.get("inputs"), dict):
            raise ValidationError(f"ComfyUI workflow node '{node_id}' or its inputs were not found")
        if input_name not in node["inputs"]:
            raise ValidationError(f"Input '{input_name}' not found on ComfyUI node '{node_id}'")
        node["inputs"][input_name] = value

    def _upload_image(self, image: Path) -> dict[str, Any]:
        boundary = f"----DarkStudio{uuid.uuid4().hex}"
        payload = image.read_bytes()
        fields = [
            (b"image", image.name.encode("utf-8")),
            (b"overwrite", b"true"),
        ]
        body = bytearray()
        for name, value in fields:
            body.extend(f"--{boundary}\r\n".encode())
            body.extend(f'Content-Disposition: form-data; name="{name.decode()}"\r\n\r\n'.encode())
            body.extend(value + b"\r\n")
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="image"; filename="{image.name}"\r\n'.encode())
        body.extend(b"Content-Type: application/octet-stream\r\n\r\n")
        body.extend(payload + b"\r\n")
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
                parsed = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"ComfyUI request failed: {exc}") from exc
        if not isinstance(parsed, dict):
            raise RuntimeError("ComfyUI returned an unexpected JSON response")
        return parsed

    def _wait_for_history(self, prompt_id: str) -> dict[str, Any]:
        deadline = time.monotonic() + self.timeout
        while time.monotonic() < deadline:
            history = self._json_request("GET", f"/history/{urllib.parse.quote(prompt_id)}")
            record = history.get(prompt_id)
            if isinstance(record, dict):
                status = record.get("status") or {}
                if status.get("status_str") == "error" or status.get("completed") is False and status.get("messages"):
                    raise RuntimeError(f"ComfyUI workflow failed: {status.get('messages')}")
                if record.get("outputs"):
                    return record
            time.sleep(self.poll_interval)
        raise TimeoutError(f"ComfyUI workflow {prompt_id} did not finish within {self.timeout:g}s")

    @staticmethod
    def _find_video_output(history: dict[str, Any]) -> dict[str, Any]:
        outputs = history.get("outputs") or {}
        for node_id, node_output in outputs.items():
            if not isinstance(node_output, dict):
                continue
            for key in ("videos", "gifs"):
                for item in node_output.get(key) or []:
                    if isinstance(item, dict) and str(item.get("filename", "")).lower().endswith(".mp4"):
                        return {**item, "node_id": str(node_id), "media_key": key}
        raise RuntimeError(
            "ComfyUI workflow finished but produced no MP4. Configure a video output node "
            "and ensure its history entry exposes outputs[*].videos or outputs[*].gifs."
        )

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
            raise RuntimeError(f"Could not download ComfyUI MP4 output: {exc}") from exc
