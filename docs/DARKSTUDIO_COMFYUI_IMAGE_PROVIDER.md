# DARKSTUDIO — ComfyUI still-image workflow

DARKSTUDIO now has two deliberately separate ComfyUI integrations:

- `ComfyUIImageProvider` submits an API-format workflow that produces a still image.
- `ComfyUIVideoProvider` remains the image-to-video provider and must produce a video clip.

Do not point the still-image setting at a video-only workflow. The image provider accepts only PNG, JPEG or WebP image outputs from the ComfyUI history response.

## Configure the still-image provider

Set these environment variables in the environment that runs the DARKSTUDIO API:

- `DARKSTUDIO_COMFYUI_URL`: ComfyUI base URL, for example `http://127.0.0.1:8188`.
- `DARKSTUDIO_COMFYUI_IMAGE_WORKFLOW`: absolute path to a ComfyUI API-format workflow JSON exported from the ComfyUI API workflow export.
- `DARKSTUDIO_COMFYUI_IMAGE_MAPPING`: JSON object mapping character IDs and prompt inputs to node IDs and input names.

Example mapping shape (the node IDs and input names below are illustrative; they must match the actual exported workflow):

```json
{
  "characters": {
    "mia": { "node_id": "12", "input": "image" },
    "leo": { "node_id": "18", "input": "image" }
  },
  "prompt": { "node_id": "25", "input": "text" },
  "negative_prompt": { "node_id": "26", "input": "text" }
}
```

The workflow must contain a separate image input for every character reference, plus the mapped positive prompt input. The negative prompt input is optional. Character mappings must be unique and cannot collide with either prompt input. Each input is populated with the filename returned by ComfyUI's `/upload/image` endpoint.

The image provider uploads each approved reference separately, submits the mapped workflow to `/prompt`, polls `/history/{prompt_id}`, downloads the still image from `/view`, and validates the downloaded file with Pillow.

## Scene generation behavior

The route `POST /jobs/{job_id}/scenes/{scene_index}/generate-character-image` now:

1. Requires explicit `character_ids` on the scene.
2. Requires an identity profile and at least one currently approved, same-project image reference for every listed character.
3. Uses ComfyUI when the still-image workflow is configured, including for scenes with multiple characters.
4. Falls back to the AUTOMATIC1111-compatible img2img adapter only for a one-character scene when ComfyUI still-image configuration is absent.
5. Rejects multi-character scenes with HTTP 503 when the ComfyUI still-image workflow is not configured; it never silently drops a character reference.
6. Stores the output as a `pending_approval` candidate. It does not replace the active scene image or invalidate the scene clip.

A reference being transmitted to a model is not proof that the generated pixels preserve identity. Candidate review remains mandatory and `pixel_identity_verified` stays false.

## Validation boundary

Automated tests use fake ComfyUI responses and temporary images. They validate request mapping, upload separation, response parsing, output file validation, and route behavior. They do not prove that a real ComfyUI installation has a compatible model, that the supplied workflow is semantically correct, or that Mia and Leo remain visually identical. A real provider smoke test requires an operator-configured workflow and running ComfyUI instance.
