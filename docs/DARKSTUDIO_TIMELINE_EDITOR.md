# DARKSTUDIO AI — Timeline editor


### Transições em projetos com cenas ComfyUI

Quando uma ou mais cenas usam vídeo generativo do ComfyUI, o renderizador misto preserva as transições da timeline:

- **Corte seco:** concatena os clipes sem remover quadros.
- **Crossfade:** mistura os últimos quadros da cena anterior com os primeiros da próxima; a sobreposição reduz a duração total pelo mesmo número de quadros na timeline.
- **Fade through black:** escurece a saída e revela a próxima cena a partir do preto, sem alterar a duração total.

A timeline, a narração por cena e as legendas usam o mesmo cálculo de sobreposição do crossfade. As transições são aplicadas pelo FFmpeg após normalizar todos os clipes para a mesma resolução, FPS e formato de pixel. O MP4 original permanece intacto; o render editado é salvo como um novo arquivo.

## Current workflow

1. Generate a video with `POST /api/v1/video-studio/videos/generate`.
2. Read its scene timeline from `GET /api/v1/video-studio/videos/jobs/{job_id}`.
3. Save edits with `PATCH /api/v1/video-studio/videos/jobs/{job_id}/timeline`.
4. Render the edited visual sequence with `POST /api/v1/video-studio/videos/jobs/{job_id}/render-edits`.

## Edit request

```json
{
  "scene_order": [1, 0, 2],
  "scene_edits": [
    {
      "scene_index": 1,
      "duration_frames": 240,
      "transition_type": "crossfade",
      "transition_duration_frames": 12
    },
    {
      "scene_index": 0,
      "duration_frames": 300,
      "transition_type": "cut"
    }
  ]
}
```

`scene_index` always refers to the original generated storyboard. The order array must contain each original scene index exactly once. Durations are frame-based and constrained to 0.5–60 seconds. Supported transitions are `cut`, `crossfade`, and `fade_through_black`; the final scene cannot have an outgoing crossfade.

## Persistence

Video jobs, source scenes, edited scenes, and timeline metadata are stored in SQLite at:

`modules/downloads/jobs/darkstudio_jobs.sqlite3`

The database uses SQLite WAL mode. It survives API process restarts when the host keeps the downloads directory on persistent storage. It is a local single-server store, not a replicated database; container deployments must mount `modules/downloads` on a persistent volume and should plan a migration to the platform's shared database before horizontal scaling.

## Audio timeline and stereo mix

The audio draft endpoint accepts separate music and sound-effect clips. The renderer mixes mono sources to dual-mono and preserves stereo sources, with per-clip left/right balance (pan: -1 left, 0 center, +1 right), trim, fades, volume and optional music looping. Speech activity can duck background music; sound effects and narration are not ducked. A linked stereo lookahead limiter reduces peaks without independently changing the left/right image.

The Audio Intelligence endpoint `POST /videos/jobs/{job_id}/audio-analysis` measures approved narration, music and SFX assets before export. It reports RMS/peak level, crest factor, silent-section ratio, clipping/near-full-scale samples, stereo balance and possible phase cancellation. Warnings are diagnostic and do not rewrite source files. When both narration and music are available, the endpoint proposes conservative ducking depth and threshold values; the editor lets the user apply the suggestion to the draft, then save it explicitly. The analysis is source-file based, not a substitute for listening to the final mix or a standards-compliant integrated loudness measurement.

Mastering presets are available for voice clarity, documentary, music and cinematic sound effects, in addition to a custom mode. A preset selects a coordinated compressor/EQ curve; custom mode preserves individually edited values. Preset identifiers are validated by the API and applied again in the renderer, so the result does not depend on browser-side state alone.

The final stereo mastering stage also supports an optional linked-channel RMS compressor and three-band EQ. The compressor exposes threshold (-60 to 0 dB), ratio (1:1 to 20:1), attack, release and makeup gain; the editor currently exposes threshold and ratio while keeping conservative attack/release/makeup defaults. The EQ exposes low, mid and high gain from -12 to +12 dB. Both stages are disabled by default and can be enabled independently. Compressor gain is linked across channels to preserve stereo balance; EQ uses smooth spectral crossovers.

Optional EBU R128 loudness normalization uses FFmpeg's two-pass loudnorm filter and measures the encoded WAV again after processing. Defaults are -14 LUFS integrated and -1 dBTP true peak. LUFS mode bypasses the separate RMS gain stage. This requires an FFmpeg build with the loudnorm filter; a missing filter is reported as an audio-render failure rather than silently skipped.

Per-clip pan is saved with the timeline metadata. Mono sources are duplicated to both channels before balance is applied; stereo sources retain their channel separation. The mix output is a two-channel WAV.

## Edited render and audio behavior

The render endpoint creates a separate MP4 file and never overwrites the original. It renders the edited visual sequence, remaps per-scene narration to the edited scene order and timing when individual scene audio is available, regenerates the SRT sidecar, and mixes the configured music and sound-effect clips.

A pre-mixed single narration track cannot be automatically re-timed after scene edits. In that case the original single track is omitted from the edited output when other audio clips are present; when no other clips exist, the status is single_track_not_retimed. Review the returned audio status rather than assuming narration was aligned.

Audio statuses:
- mixed_audio: narration and configured music/effects were mixed.
- mixed_audio_single_track_omitted: configured music/effects were mixed, but the original pre-mixed narration could not be re-timed and was omitted.
- single_track_not_retimed: the original pre-mixed narration was not re-timed.
- silent: no audio clips were configured.
- audio_mux_failed: visual MP4 succeeded but audio muxing failed.

Subtitle statuses are returned separately; when regeneration succeeds, the edited SRT follows the edited scene timing. The edited video remains a separate output from the original generated MP4.

## Final audio quality control

Every edited render with mixed audio now returns and persists an `edit_render_quality` report. It measures the final stereo mix after ducking, compressor, EQ, normalization and limiting. The report includes final peak/RMS, clipping ratio, internal silence gaps of at least 500 ms, and windows where the music stem is less than 6 dB below active narration. Stem comparison uses 100 ms RMS energy windows and is explicitly heuristic; it is not speech recognition or a perceptual masking model.

- `passed`: no configured quality warnings were detected.
- `needs_review`: export is allowed, but silence gaps, possible narration masking or pre-limiter overload should be reviewed.
- `blocked`: the final encoded mix contains full-scale clipped samples; MP4 muxing is stopped with HTTP 422 until the mix is corrected.

The report also includes explicit correction suggestions. When narration may be masked, the editor offers a one-click increase to ducking depth; it changes only the editable audio draft and must be saved before another render. Gain-reduction suggestions remain advisory, and silence gaps are never removed automatically.

The editor displays the report after rendering and can restore it from job status. Expected pauses may be intentional; users should review the listed timestamps rather than automatically deleting silence. Pre-limiter overload is a warning because the final limiter may correct it; actual clipping in the final mix is the export-blocking condition.

## API response statuses

- edit_draft_status: persisted_local_sqlite means scene edits were stored in the local SQLite database.
- edit_render_status: rendering | completed | failed | quality_blocked describes the edited MP4 lifecycle.
- audio_status: use the values above; it is not a generic guarantee that the original narration was retained.


## A/V Sync Intelligence

The editor exposes `POST /videos/jobs/{job_id}/av-sync-analysis` and the **Verificar A/V** action. The analyzer compares narration clip ranges with video scene ranges using integer frames and the project FPS. It reports scene start/end offsets, long narration gaps, overlaps, and narration extending beyond the video. A two-frame tolerance is used by default; intentional crossfade overlaps are accounted for when comparing scene ends.

The report is persisted on the job as `av_sync_analysis` and is restored when reopening the editor. Critical narration ranges outside the video are reported as blocked; ordinary timing mismatches and long gaps require review.

**Scope limitation:** this is timeline metadata validation only. It does not inspect acoustic speech onsets, lip movements, dialogue semantics, or actual mouth synchronization. A waveform/forced-alignment or audiovisual model would be required for those checks. It does not silently shift or trim clips.


## Visual Intelligence Engine

The editor adds **Analisar qualidade visual**, backed by `POST /videos/jobs/{job_id}/visual-analysis`. The report is persisted as `visual_intelligence` on the job and is restored when reopening the editor.

The deterministic metadata heuristic is studio-aware:
- **Whymentary:** explanatory text/primitive clarity, animated elements, shot variety, and restrained camera motion.
- **Historical Documentary:** camera movement coverage, composition richness, shot variety, and scene continuity metadata.

Per-scene diagnostics include shot type, camera keyframe deltas, animated primitive counts, primitive/particle counts, text presence, and character IDs. Warnings include static scene descriptors, long unchanged shots, consecutive repeated compositions, low shot variety, and character-ID changes. The engine records selected character and prop IDs on every planned scene to make identity changes auditable.

The 0–100 score is explicitly a heuristic over scene descriptors. It is **not** computer vision: it does not inspect encoded MP4 pixels, assess actual artistic quality, verify faces, or prove visual continuity. Review the rendered video before publication; the report never edits scenes automatically.


## Encoded MP4 Scene Intelligence

The editor adds **Analisar MP4 renderizado**, backed by `POST /videos/jobs/{job_id}/mp4-visual-analysis`. It inspects the latest edited MP4 when available, otherwise the original rendered MP4. FFprobe reads the real duration; FFmpeg extracts up to 48 evenly sampled frames, resized to 160×90. Pillow/NumPy compute adjacent-frame pixel change, perceptual difference hash, RGB histogram similarity, and a 4×4 luminance-grid change proxy.

The report flags near-duplicate sampled frames and sustained low-change runs, and maps sampled comparisons to video timeline clips when clip timing is present. The sampling is bounded and configurable from 3 to 120 frames at the API boundary.

**Interpretation limits:** this is not semantic computer vision. It cannot identify Mia/Leo, recognize faces or props, infer whether motion is meaningful, or judge artistic quality. Pixel change may come from camera movement, object movement, compression noise, or scene cuts. Issues between sampled timestamps can be missed. Use the report to locate sections for human review, not as an automatic export gate.


## Prompt-driven scene images and VidGrid clips

The text-to-video pipeline now supports `scene_image_mode`:
- `procedural`: existing SceneCanvas-generated scenes; no diffusion model required.
- `ai`: generate one independent image for each storyboard scene using a configured local AUTOMATIC1111-compatible Stable Diffusion WebUI API. A missing/unavailable model is an explicit job failure.
- `auto`: attempt local image generation and record procedural fallbacks per scene when the image service is unavailable.

Configure `DARKSTUDIO_IMAGE_API_URL` (default `http://127.0.0.1:7860`) and start the compatible WebUI with its API enabled. The default image maximum edge is 768px for lower-VRAM GPUs; set `DARKSTUDIO_IMAGE_MAX_EDGE` to 1024 or higher only when the installed GPU/model can handle it. The adapter calls `/sdapi/v1/txt2img` for scene plates and `/sdapi/v1/img2img` for text-directed image edits. ComfyUI workflow JSON, cloud providers, and model downloads are not implemented by this adapter yet. No model is bundled with DARKSTUDIO.

Every scene receives its own `visual_prompt`, `negative_prompt`, narration text and shot type from the storyboard. The generated still is rendered as a background image; SceneCanvas keeps camera moves, particles, overlays, and optional procedural cast on top. The background is cached per render canvas to avoid reopening the source image on every frame.

The editor exposes per-scene text instructions. It edits the existing scene image with img2img when available, or creates a new image with txt2img when the scene had no generated image. The updated asset is stored on the edited scene; the user must run **Renderizar edição** to produce a new MP4. The original render remains unchanged.

**VidGrid compatibility:** the UI enables `vidgrid_compatible` by default. In this mode each storyboard clip is exactly 10 seconds, up to 60 clips per job, and total duration is `scene_count × 10` seconds (up to 10 minutes). The pipeline exports both the assembled full MP4 and one separate MP4 per scene under `downloads/videos/vidgrid_clips/`. Per-scene TTS audio is muxed into its matching ten-second clip when available; flat single-track narration is not automatically split, and the clip manifest labels that condition. Disabling the option restores free total-duration planning.

**Honest capability boundary:** this pipeline currently generates still images per scene and animates them with camera moves, transitions, particles, overlays, and synchronized narration. It does not yet run a per-frame text-to-video diffusion model such as Wan. The existing style-specific image generators still use procedural SceneCanvas templates; their style names do not mean they run a diffusion model. The new local diffusion adapter is the actual text-to-image / image-to-image path. Stable character identity across diffusion-generated images is not yet guaranteed by this basic img2img integration; recurring vector characters remain a separate overlay system.


### Prompt-driven scene imagery

New video jobs default to `scene_image_mode=auto`. The storyboard planner supplies a separate visual description for each scene; the engine sends each description to the configured local Stable Diffusion WebUI-compatible image API and stores the generated image as that scene's background plate. If the local image service is unavailable, automatic mode records a procedural fallback for that scene. Choose `ai` to require image generation and fail rather than silently falling back, or `procedural` to avoid a diffusion server. The recurring Mia/Leo vector cast remains a separate optional overlay, not the source of every scene image.

## Image-to-video motion engine

The image-to-video engine now streams frames directly to FFmpeg instead of
materializing an entire clip in memory. It supports eased camera moves:
`push_in`, `pull_out`, `pan_left`, `pan_right`, `tilt_up`, `tilt_down`,
`orbit`, `parallax`, and `handheld` (the older `zoom` and `pan` names
remain aliases). The engine validates the preset and requires an MP4 encoder
for this output path.

These are deterministic pixel/camera animations of the supplied still image,
not diffusion-generated motion. They do not synthesize new body movement,
facial acting, lip-sync, or new objects between frames. A true generative
image-to-video provider (for example a configured Wan workflow) is not yet
connected to this production pipeline. This distinction is intentional: the
UI and job metadata must not label a camera move as AI-generated video.

### Optional generative image-to-video through ComfyUI

The dedicated image-to-video endpoint accepts `motion_provider=camera` (default)
or `motion_provider=comfyui`. ComfyUI mode requires a running ComfyUI server,
an API-format workflow JSON exported from that installation, and a node mapping.
No Wan graph or custom-node IDs are assumed by the application.

Configure the backend environment:

- `DARKSTUDIO_COMFYUI_URL=http://127.0.0.1:8188`
- `DARKSTUDIO_COMFYUI_WORKFLOW=C:/path/to/workflow_api.json`
- `DARKSTUDIO_COMFYUI_MAPPING={"image":{"node_id":"LOAD_IMAGE_NODE","input":"image"},"prompt":{"node_id":"POSITIVE_PROMPT_NODE","input":"text"},"negative_prompt":{"node_id":"NEGATIVE_PROMPT_NODE","input":"text"}}`

Replace the node IDs and input names with those from the actual workflow's API
export. The workflow must accept an uploaded image and prompt and expose an MP4
file in ComfyUI history under `outputs[*].videos` or `outputs[*].gifs`.
Workflows that only output PNG frames are rejected rather than mislabeled as
video generation.

Example request to `POST /videos/image-to-video` (under the API prefix configured by the application):

```json
{
  "image_ref": "C:/assets/scene-01.png",
  "duration_seconds": 10,
  "fps": 24,
  "motion_provider": "comfyui",
  "motion_prompt": "Slow cinematic orbit around the subject; preserve identity and clothing",
  "negative_prompt": "flicker, deformation, extra limbs"
}
```

The returned MP4 is conformed to the requested duration, frame rate and
resolution by FFmpeg. If the generated source is shorter, it is looped to fill
the requested clip; if longer, it is trimmed. This duration conforming does not
guarantee seamless motion at the loop boundary. The endpoint is an explicit
opt-in and the regular DARKSTUDIO text-to-video storyboard pipeline remains
unchanged until a tested scene-by-scene video provider is integrated there.

For Wan, use an API-exported workflow that is already installed and tested in
your ComfyUI environment. On a GTX 1060 6 GB, modern Wan video workflows are
not a realistic local-generation target; use a remote ComfyUI server or a
smaller compatible model. The backend adapter itself adds no model weights.


## Integração de clipes generativos à timeline

A geração de movimento ComfyUI pode ser iniciada dentro de uma cena já existente:
- `POST /videos/jobs/{job_id}/scenes/{scene_index}/motion` recebe o prompt de movimento e usa a imagem da própria cena.
- O MP4 normalizado é associado à cena em `_edited_scenes` e persistido no SQLite; o status do trabalho expõe os metadados em `scene_clips`.
- Ao renderizar a edição, cenas com `generative_video_path` usam o MP4 ComfyUI; as demais são renderizadas pelo motor de cenas do DARKSTUDIO.
- Todos os clipes são normalizados para resolução, FPS e contagem de frames da cena antes da concatenação. No modo VidGrid, a cena continua com 10 segundos exatos.
- O MP4 editado é um novo arquivo; o MP4 original não é sobrescrito.

**Limitação atual de montagem mista:** o assembler concatena com cortes secos. Se a timeline tiver crossfade ou fade-through-black, esses efeitos são convertidos em cortes secos quando há pelo menos um clipe generativo. A EDL, os offsets de narração por cena e as legendas são recalculados com esse mesmo tempo de corte para evitar dessincronização. O renderer tradicional continua aplicando as transições quando nenhuma cena usa clipe generativo.

A geração exige ComfyUI e workflow API configurados no servidor. O endpoint não inicia nem instala o ComfyUI automaticamente.
