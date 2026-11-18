# DARKSTUDIO AI — Timeline editor

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

## API response statuses

- edit_draft_status: persisted_local_sqlite means scene edits were stored in the local SQLite database.
- edit_render_status: rendering | completed | failed describes the edited MP4 lifecycle.
- audio_status: use the values above; it is not a generic guarantee that the original narration was retained.
