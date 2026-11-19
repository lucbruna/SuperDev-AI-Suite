# DARKSTUDIO AI — Timeline editor



### Pré-visualização da montagem

O botão **Pré-visualizar montagem** gera um proxy MP4 do rascunho salvo, limitado a 640 px na maior dimensão e 12 FPS. A prévia usa o mesmo renderizador de cenas procedurais ou misto com clipes ComfyUI, incluindo as transições configuradas. Ela é salva como arquivo separado e não substitui o vídeo original nem o render final.

A prévia é visual: não faz mixagem de narração, música ou efeitos e não queima legendas no vídeo. Use-a para revisar ordem, imagens, enquadramentos e transições; valide áudio e legendas no MP4 final. O botão exige que o rascunho visual e as alterações de áudio estejam salvos.

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


## Diretor visual por cena e regeneração pontual

- `GET /videos/jobs/{job_id}/visual-direction` retorna a narração, o papel narrativo, o enquadramento, a direção de composição e a sugestão de prompt por cena.
- O editor apresenta a justificativa do plano e preenche o prompt sugerido; o usuário pode alterá-lo antes de gerar a imagem.
- `POST /videos/jobs/{job_id}/scenes/{scene_index}/image-edit` regenera somente a imagem da cena selecionada. O endpoint usa o índice estável da cena original mesmo quando a timeline foi reordenada.
- A regeneração preserva o restante do storyboard e do MP4 original. O clipe VidGrid correspondente pode ser atualizado separadamente; para refletir a imagem no vídeo completo, é necessário renderizar a edição.
- O diretor não inventa fatos históricos: sugestões visuais são derivadas do texto narrado e identificadas como instruções de composição, não como novas afirmações factuais.
- O perfil Whymentary mantém fundo branco, formas 2D e cores chapadas; Historical Documentary mantém ilustração cinematográfica, profundidade e luz atmosférica.

## Storyboard cinematográfico e continuidade visual

O pipeline de texto para vídeo agora executa um planejador de storyboard antes da geração das imagens. Cada cena recebe um identificador estável, um prompt visual completo, restrições negativas e metadados de continuidade (personagens, objetos, ambiente, figurino e período do dia quando esses dados foram fornecidos no roteiro).

- O texto de narração original é preservado; o planejador não o reescreve.
- Prompts visuais são específicos por cena e incluem direção de composição do diretor cinematográfico.
- O relatório do storyboard sinaliza cenas sem descrição/narração e conceitos visuais repetidos para revisão.
- O estúdio Histórico inclui uma restrição explícita para não apresentar detalhes inventados como fatos históricos.
- As restrições negativas são aplicadas tanto à geração inicial quanto à regeneração pontual da imagem.
- A API `GET /videos/jobs/{job_id}/visual-direction` expõe o ID da cena, prompt completo, prompt negativo, continuidade e estado de revisão sem revelar caminhos internos.

O relatório fica disponível em `storyboard_report` no estado do job. A detecção de repetição é textual/determinística; ela não é análise visual por visão computacional e não garante que duas imagens geradas sejam visualmente diferentes.

## Regeneração em lote de cenas selecionadas

O editor permite marcar cenas individualmente ou selecionar todas e solicitar regeneração em lote. A interface envia apenas os índices selecionados e os prompts correspondentes para `POST /videos/jobs/{job_id}/scenes/regenerate`.

- O servidor processa as cenas sequencialmente para evitar picos simultâneos de VRAM e carga no provedor de imagens.
- Cada cena mantém seu próprio resultado; uma falha não apaga as imagens que já foram atualizadas.
- A resposta informa quantidade solicitada, sucessos, falhas e erro por cena.
- O editor atualiza as miniaturas das cenas concluídas e mantém as falhas identificadas.
- Em modo VidGrid, cada cena atualizada tenta reconstruir seu clipe de exatamente 10 segundos; se essa renderização falhar, a imagem continua salva e o clipe é marcado como desatualizado.
- A regeneração de imagens não atualiza automaticamente o MP4 completo: é necessário renderizar a edição após revisar as imagens.

O lote aceita até 60 cenas por solicitação e rejeita índices duplicados. A execução é sequencial, não transacional: resultados concluídos são preservados mesmo se outra cena falhar.


## Aprovação de imagens candidatas

A regeneração individual e em lote pode operar em modo de pré-visualização. Nesse modo, a imagem gerada é salva como candidata pendente e não substitui a imagem ativa da cena. A interface mostra a imagem atual e a candidata lado a lado; somente **Aprovar nova imagem** chama `POST /videos/jobs/{job_id}/scenes/{scene_index}/image-candidates/{candidate_id}/approve` e promove o arquivo para a cena. Candidatas não aprovadas permanecem separadas da timeline. Após a aprovação, o clipe VidGrid daquela cena é marcado como desatualizado e o MP4 completo precisa ser renderizado novamente. A aprovação é persistida no registro do job.


## Detecção de imagens repetidas por pixels

A ação **Detectar imagens repetidas** compara os arquivos de imagem ativos das cenas, não os textos dos prompts. O serviço calcula SHA-256 para duplicatas binariamente idênticas e um difference hash (dHash) de 64 bits para sinalizar imagens estruturalmente semelhantes, com distância de Hamming configurável (padrão 6). A execução é CPU/Pillow e não requer GPU nem serviço de IA. O relatório lista os pares de cenas e o percentual de similaridade estrutural. Isso não é reconhecimento semântico: imagens diferentes do mesmo assunto podem ser sinalizadas, e imagens visualmente relacionadas com composição alterada podem escapar. A análise é consultiva e não exclui nem substitui arquivos automaticamente.
 O botão **Manter imagem atual** descarta a candidata pendente sem alterar a imagem ativa da cena.


## Bíblia de personagens e auditoria de continuidade

O storyboard injeta instruções de identidade estáveis para personagens conhecidos: Leo (cabelo loiro, camisa azul, calça escura) e Mia (cabelo castanho preso, vestido vermelho). O perfil é acrescentado ao prompt completo de cada cena selecionada, além das restrições negativas contra alteração de identidade. A análise de continuidade compara personagens declarados por cena e descrições de aparência/figurino fornecidas em `character_appearance` ou `character_costumes`; sinaliza mudanças de elenco e divergências de aparência, com índices exatos das cenas. O relatório é exposto na API de direção visual e no editor.

**Limite importante:** esta etapa é uma auditoria de metadados e instruções de geração, não reconhecimento de personagens nos pixels. Ela melhora a consistência solicitada ao gerador, mas não certifica que a imagem gerada respeitou a bíblia visual. A revisão visual continua necessária.


## Generation preflight

Before submitting a new render, the dashboard calls `POST /videos/preflight` with the same generation parameters. The response contains:

- MP4 encoder availability (FFmpeg), FFprobe availability, and whether the local image endpoint / ComfyUI workflow have configuration values.
- A hard blocker when FFmpeg is missing, plus warnings for optional or unverified services.
- The calculated duration, frame budget, resolution and FPS. In VidGrid mode the estimate is exactly `scene_count × 10 seconds`, with ten-second clip duration.

The dashboard stops before queueing when `can_queue=false` and displays warnings when the configuration is usable but incomplete. The preflight deliberately does not claim that an HTTP endpoint, model, TTS voice, GPU or ComfyUI workflow is reachable or operational; those checks require runtime/provider-specific health probes. An endpoint marked `configured_unverified` is configuration evidence only, not a successful model test.

Example:

```http
POST /api/v1/video-studio/videos/preflight
Content-Type: application/json
```

Use the same request body as `POST /videos/generate`. A successful preflight does not reserve resources or create a job; generation is still submitted separately.


## Job checkpoints and restart recovery

The generation API persists periodic render-progress checkpoints in SQLite (first checkpoint, approximately every two seconds / two seconds of frames, and the final frame). This reduces the amount of progress lost if the API process stops during a long render without creating a database transaction for every frame.

On API startup, jobs left in `queued` or `processing` are marked `failed` with `interrupted=true`, preserving their last saved progress and an explanation. This is explicit recovery, not automatic render resumption: FFmpeg and external model subprocess state is not checkpointed, so a new job must be started. Completed jobs and editable timelines are not changed by this recovery pass.


## Final MP4 validation

Completed jobs expose `POST /videos/jobs/{job_id}/validate-output`. The endpoint confines inspection to the DARKSTUDIO video output directory and invokes FFprobe with an argument list (no shell) to inspect the container, duration, video stream, dimensions/FPS metadata and audio stream count. The report is persisted on the job and includes file size, errors and warnings.

The dashboard provides a **Validar MP4** action next to the download link. A report is marked valid only when the file exists, is non-empty, FFprobe is available, and a video stream plus positive duration are confirmed. Audio is reported but not required, because silent videos are legitimate outputs. A duration mismatch is a warning, not an automatic rejection: transitions and timeline edits can change the final runtime.

This check confirms container/stream readability, not visual quality, narration intelligibility, subtitle correctness, or whether the scene images match the script. Those require separate semantic and human review.

## Reconstrução seletiva de clipes VidGrid

O endpoint `POST /videos/jobs/{job_id}/scenes/rebuild-stale-clips` reconstrói somente os clipes marcados como `stale` após a aprovação de uma nova imagem. Para cada cena, reutiliza a imagem aprovada, as configurações do estúdio e a narração por cena já existente; não solicita novas imagens nem recria a narração. O resultado substitui o registro do clipe daquela cena e preserva os demais clipes.

- Disponível somente para jobs concluídos no modo VidGrid.
- Cada clipe reconstruído mantém exatamente 10 segundos.
- Falhas são reportadas por cena; clipes atualizados com sucesso são preservados mesmo se outra cena falhar.
- Operações concorrentes de edição, regeneração em lote e render final são bloqueadas enquanto a reconstrução seletiva está ativa.
- A reconstrução dos clipes não concatena o MP4 completo. Depois dela, ainda é necessário chamar `POST /videos/jobs/{job_id}/render-edits` para gerar o vídeo final.

## Bloqueio seguro entre regeneração e render

A API agora impede alterações de imagens/candidatas enquanto o MP4 editado está sendo renderizado e impede iniciar o render final enquanto uma regeneração em lote ainda está ativa. A aprovação de candidatas também é bloqueada durante uma operação de lote. Essas respostas usam HTTP 409 para que a interface possa orientar o usuário a aguardar, em vez de permitir que o render leia um storyboard que está sendo alterado simultaneamente.

Isso protege a consistência do snapshot de cenas usado pelo FFmpeg. Não implementa fila automática nem cancelamento: o usuário deve repetir a ação depois que a operação ativa terminar.

## Progresso e recuperação por cena

Cada job expõe agora `scene_progress`, uma lista persistida de estados individuais. O motor emite eventos após planejar o storyboard, durante a geração de imagem e durante a exportação de cada clipe VidGrid. O backend atualiza o registro do job em cada evento; falhas de persistência do telemetria não interrompem o render.

Estados observáveis: `pending`, `processing`, `completed`, `fallback` e `failed`. As etapas incluem `storyboard`, `image_generation`, `image_ready`, `image_fallback`, `clip_render`, `clip_ready` e `exported`. A interface apresenta a grade de cenas e a contagem de cenas concluídas, preservadas ao recarregar a lista de jobs.

Limite atual: este lote implementa rastreamento e diagnóstico por cena, não a repetição isolada de uma cena. A regeneração seletiva exige ainda uma operação que reutilize o storyboard/ativos originais, invalide somente o ativo escolhido e remonte o vídeo final; não deve ser confundida com o status visual já disponível.



### Montagem final otimizada do VidGrid

Quando todas as cenas possuem clipes atualizados, cada clipe é validado com FFprobe (arquivo, codec, resolução, FPS, pixel format e duração de 10 segundos). Se a edição usar apenas cortes secos e os arquivos forem compatíveis, o motor concatena os fluxos de vídeo com FFmpeg em modo stream-copy, sem reencodificar os clipes. O áudio embutido nos clipes individuais é descartado nessa junção; narração por cena, música e efeitos são mixados novamente na timeline final para evitar duplicação de voz.

Se houver transições, incompatibilidade técnica ou metadados fora do padrão, o sistema usa o renderizador misto com os próprios clipes VidGrid como fontes, reencodificando somente a montagem necessária para aplicar transições. Clipes ausentes ou marcados como stale bloqueiam a exportação final e exigem reconstrução seletiva antes de continuar. Entradas do caminho stream-copy são confinadas ao diretório de vídeos do DARKSTUDIO.

### Ação na interface

O painel da timeline consulta os clipes do job e exibe **Reconstruir N clipe(s) VidGrid** somente quando há clipes marcados como desatualizados. A ação chama o endpoint seletivo, bloqueia edição/render concorrente, atualiza a contagem após a operação e apresenta o resumo de sucesso parcial/falha. A aprovação de uma imagem candidata atualiza a contagem sem exigir recarregar a página.

A regeneração em lote de imagens também respeita o bloqueio de reconstrução seletiva, evitando que a imagem ativa seja trocada enquanto o clipe correspondente está sendo reconstruído. A reconstrução seletiva continua sendo apenas a etapa dos clipes individuais; o botão **Renderizar edição** segue responsável por produzir o MP4 completo.


### Manifesto e validação técnica da exportação

Cada render final da timeline persiste um manifesto com o modo de montagem (concatenação VidGrid sem reencodificação, montagem VidGrid com transições, clipes generativos ou render procedural), índices das cenas-fonte, fallback utilizado, frames produzidos, FPS/resolução-alvo e estados de áudio/legendas.

O endpoint `POST /videos/jobs/{job_id}/validate-output` valida a exportação editada mais recente antes de recorrer ao MP4 original. Quando FFprobe está disponível, registra duração, contagem de streams, codecs, resolução, FPS, pixel format, dados básicos do áudio e integridade estrutural do vídeo. Também alerta sobre áudio ausente quando a etapa não foi declarada silenciosa, falha de mux, faixa única não reposicionada, divergência de duração e sidecar de legendas ausente.

A validação é estrutural, não uma prova de sincronização perceptual, inteligibilidade da fala ou qualidade visual. A existência do arquivo SRT é verificada separadamente; o SRT não é presumido como faixa embutida no MP4. Sem FFprobe, o relatório marca a integridade como não verificada, em vez de aprovar o arquivo.


### Plano de recuperação inteligente por cena

O endpoint `GET /videos/jobs/{job_id}/recovery-plan` faz uma auditoria não destrutiva das cenas VidGrid. Para cada cena compara a imagem aprovada ativa com o fingerprint SHA-256 salvo no clipe, verifica a existência e a localização segura do MP4 e compara resolução/FPS com o perfil atual. Também detecta clipes ausentes e estados explicitamente stale.

O painel consulta esse plano e mostra quantas cenas estão prontas, quantas precisam de reconstrução e quantas estão bloqueadas por falta de imagem válida. A ação de recuperação reconstrói somente cenas reparáveis, preservando os clipes ainda válidos. Depois da reconstrução, o fingerprint da imagem é persistido para permitir detectar alterações futuras. Jobs antigos sem fingerprint são sinalizados como legado, sem serem invalidados automaticamente apenas por isso.

Limite: a verificação usa fingerprint da imagem e metadados/arquivo do clipe; não faz comparação semântica dos frames renderizados nem valida a integridade interna de cada clipe com FFprobe nesta etapa. A recuperação dos clipes individuais não substitui a renderização do MP4 completo.


## Fila persistente e reconstrução selecionada de clipes VidGrid

O endpoint `POST /videos/jobs/{job_id}/scenes/rebuild-stale-clips` aceita opcionalmente `{"scene_indices":[0,3]}` para reconstruir somente cenas reparáveis selecionadas. Sem esse corpo, reconstrói todas as cenas reparáveis retornadas por `GET /videos/jobs/{job_id}/recovery-plan`. Índices que não estejam no plano de reparo são rejeitados com HTTP 422; cenas prontas nunca são reprocessadas por engano.

Durante a execução, o job persiste `scene_clip_rebuild_queue` com índices solicitados, total, concluídos, falhas, cena atual, resultados e timestamps. O estado também é incluído no modelo de status do job. Se a API reiniciar enquanto a fila estiver em processamento, o estado é marcado como `interrupted`; clipes já concluídos permanecem salvos e o usuário pode consultar novamente o plano e reenviar somente os índices ainda reparáveis.

**Limite atual:** a fila é persistente e recuperável por reenvio, mas a execução ainda é síncrona dentro da requisição HTTP. Não há cancelamento cooperativo, worker independente nem retomada automática do processo interrompido. A reconstrução dos clipes continua exigindo uma exportação final do MP4 completo.


## DARKSTUDIO Asset Intelligence — auditoria de saúde

O endpoint `GET /videos/jobs/{job_id}/asset-health` executa uma auditoria somente leitura dos ativos referenciados pelo job: imagens de fundo das cenas, clipes VidGrid, narração individual, músicas e efeitos configurados na timeline. Os caminhos são confinados às pastas específicas do subsistema (`images`, `videos`, `voice`, `music` e `effects`); caminhos externos não são expostos no relatório.

Cada referência recebe um estado `available`, `missing`, `corrupt` ou `unreadable`. Arquivos existentes e não vazios recebem tamanho e SHA-256. O painel da timeline apresenta contagens e lista as cenas/faixas que precisam de atenção.

**Limites:** a auditoria não decodifica cada quadro de MP4, não verifica se a imagem corresponde semanticamente ao roteiro, não mede sincronização perceptual e não recria ativos automaticamente. Arquivos com extensão válida, mas conteúdo inválido, podem exigir FFprobe/decodificação específica em uma etapa posterior. Narração em faixa única não é artificialmente atribuída a cenas individuais.


### Verificação de integridade dos arquivos de mídia

A auditoria `GET /videos/jobs/{job_id}/asset-health` agora tenta validar clipes de vídeo, narrações, músicas e efeitos com FFprobe quando o executável está instalado. Arquivos rejeitados pelo FFprobe, sem stream esperado ou sem duração válida são classificados como `corrupt`; falhas ao executar a inspeção são classificadas como `unreadable`. Sem FFprobe, o arquivo permanece como disponível pela verificação básica de existência/tamanho/SHA-256, mas recebe `probe_status=not_verified` — isso não significa que o conteúdo foi decodificado ou validado.


### Grafo de dependências da produção

O endpoint `GET /videos/jobs/{job_id}/dependency-graph` descreve as dependências persistidas por job: imagem aprovada → clipe da cena; narração por cena → clipe quando o áudio é muxado individualmente; clipes e faixas de áudio → exportação final. A resposta inclui nós, relações, estado básico dos ativos e regras de impacto para orientar reconstruções seletivas.

O editor de timeline oferece o botão **Mapa de dependências** e apresenta a contagem de ativos/relações e as regras de reconstrução. Esta versão é somente de leitura: não dispara renders nem altera arquivos. Alterações de música/efeitos apontam para reconstrução da exportação final; alterações de imagem/narração por cena apontam para o clipe correspondente e a exportação.


## Prévia de impacto das dependências

O endpoint `POST /videos/jobs/{job_id}/dependency-impact` recebe `changed_asset_ids` e percorre o grafo persistido para calcular os nós downstream afetados. A resposta informa as cenas que exigem reconstrução de clipe e se a exportação final precisa ser refeita. IDs que não pertencem ao job são rejeitados com HTTP 422.

A interface do editor permite selecionar imagens, narrações, músicas, efeitos ou clipes existentes e solicitar essa prévia. O resultado é somente leitura: `executed=false` e `requires_user_confirmation=true`. Nenhuma geração ou renderização é iniciada. A execução continua separada nos comandos existentes de reconstrução seletiva VidGrid e renderização final; alterações em músicas/efeitos afetam somente a exportação final segundo o grafo registrado.

Limitações: o plano depende das relações persistidas e não identifica arquivos externos não registrados. O endpoint ainda não executa uma transação única para reconstruir clipes e exportar o MP4.


## Fingerprints e detecção de ativos alterados

A timeline de áudio persiste `_audio_clips.music` e `_audio_clips.sfx`; `audio_settings` contém os parâmetros de mixagem, não as referências das faixas. A auditoria e o grafo agora leem a estrutura canônica `_audio_clips`, com fallback para jobs legados que tenham referências no formato antigo.

Ao salvar a timeline de áudio, cada música/efeito recebe um SHA-256 de referência (`asset_fingerprint`). O grafo calcula o SHA-256 atual e marca o nó como `stale` se o arquivo tiver sido substituído ou alterado depois de salvo. Para clipes de cena, o fingerprint da imagem aprovada é comparado com `source_image_fingerprint` registrado no clipe; divergências marcam a imagem de origem como alterada, permitindo selecionar a imagem e planejar a reconstrução do clipe dependente.

A interface oferece **Selecionar ativos alterados** para selecionar automaticamente nós `stale` antes de calcular o impacto. Essa seleção e a prévia não executam renderização. Jobs antigos sem fingerprint de áudio permanecem sem verificação histórica até que suas faixas sejam salvas novamente.


## Recuperação por alteração de narração por cena

Para jobs com `narration_style=per_scene`, o plano de recuperação agora compara o SHA-256 do áudio atual com `source_narration_fingerprint` salvo no clipe VidGrid. Se a narração mudar, a cena recebe o motivo `source_narration_changed` e entra na lista de reconstrução, desde que a imagem aprovada esteja disponível. A auditoria de saúde e o grafo de dependências também marcam o nó de narração como `stale`, propagando o impacto para o clipe da cena e para a exportação final.

Ao reconstruir o clipe, o sistema valida que o arquivo de narração está dentro do diretório aprovado de voz, faz o mux e registra o novo fingerprint. Clipes legados sem esse fingerprint recebem um aviso de verificação histórica ausente; não são considerados alterados apenas por falta de metadados. A reconstrução continua limitada a clipes de cena; a renderização do MP4 final é uma etapa separada.


## Execução confirmada do plano de dependências

A prévia pode ser executada pelo endpoint `POST /videos/jobs/{job_id}/execute-dependency-rebuild`, enviando os mesmos `changed_asset_ids` e `confirmed: true`. O servidor recalcula o impacto no momento da execução; não confia cegamente na prévia exibida anteriormente. A operação bloqueia ativos ausentes, corrompidos ou ilegíveis, reconstrói somente os índices de cena afetados e chama a exportação final depois que todos os clipes selecionados forem concluídos.

Quando a alteração afeta apenas música ou efeitos, nenhum clipe de cena é reconstruído: a timeline de áudio é reutilizada e somente o MP4 final é renderizado. Se qualquer reconstrução de cena falhar, o endpoint retorna `partial` e não publica uma nova exportação final incompleta. A execução exige confirmação explícita, registra estado e resultados no job e impede uma segunda execução simultânea. Em reinício da API, uma execução que ainda constava como `processing` é marcada como `interrupted`; o usuário deve revisar o grafo e o plano de recuperação antes de tentar novamente.

A interface apresenta o botão **Confirmar e executar reconstrução** somente após uma prévia indicar que a exportação final é necessária. A operação é síncrona nesta versão: o cliente aguarda a conclusão da reconstrução e renderização, sem progresso em tempo real nem cancelamento cooperativo. Uma interrupção do cliente não equivale a cancelamento garantido do trabalho no servidor.


A seleção direta de um nó `video_clip` também inclui a própria cena no plano de reconstrução (não apenas a exportação downstream). Arquivos de clipe ausentes ou corrompidos são tratados como saídas reconstruíveis; o bloqueio é reservado às entradas necessárias — imagem, narração, música e efeitos — quando ausentes, corrompidas ou ilegíveis.


## Fila assíncrona de reconstrução VidGrid

A reconstrução seletiva também pode ser iniciada sem manter a requisição HTTP aberta:

- `POST /videos/jobs/{job_id}/scenes/rebuild-stale-clips/queue` retorna HTTP 202 e um `queue_id`.
- `GET /videos/jobs/{job_id}/scenes/rebuild-stale-clips/status` retorna status, cena atual, totais, resultados e erros.
- `POST /videos/jobs/{job_id}/scenes/rebuild-stale-clips/cancel` solicita cancelamento cooperativo. A cena que já começou termina; as próximas não são iniciadas.
- A fila e os resultados por cena são persistidos no job. O frontend inicia a fila e oferece atualização manual de progresso e cancelamento.

Os locks são adquiridos antes do agendamento, impedindo edições, renderização e outra reconstrução enquanto a tarefa aguarda execução. Em reinicialização da API, filas em `queued` ou `processing` são marcadas como `interrupted`; resultados já concluídos permanecem salvos. A retomada é manual nesta versão: consulte o recovery-plan e enfileire apenas as cenas que continuarem reparáveis. O worker usa `BackgroundTasks` do processo FastAPI; não é ainda uma fila distribuída nem garante execução após encerramento abrupto do processo.
