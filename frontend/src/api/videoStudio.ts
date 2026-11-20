import apiClient from "./client";

// ---------------------------------------------------------------------------
// AI Video Studio API client — connects the dashboard to the real module
// backend mounted at /api/v1/video-studio (see backend/app.py).
// ---------------------------------------------------------------------------

const STUDIO_BASE = "/video-studio";

export interface StudioProfile {
  id: "whymentary" | "historical_documentary" | "felt_clay";
  name: string;
  visual_language: string;
  background: { type: string; colors: string[] };
  palette: string[];
  noise: number;
  grading_strength: number;
  text: { default_color: string; default_size: number };
  camera_defaults: Record<string, number>;
}

export interface StudioCharacter {
  id: string;
  name: string;
  studio_id: StudioProfile["id"];
  appearance: Record<string, string | boolean>;
  supported_poses: string[];
  supported_expressions: string[];
}

export interface StudioSceneObject {
  id: string;
  name: string;
  studio_id: StudioProfile["id"];
  category: string;
  description: string;
}

export interface StudioHealth {
  status: string;
  service: string;
  version: string;
}

export interface StudioVoice {
  id: string;
  name: string;
  gender: string;
  language: string;
  style?: string[];
  description?: string;
}

export interface EditTimelineClip {
  start_frame: number;
  end_frame: number;
  duration_frames: number;
  start_seconds?: number;
  end_seconds?: number;
  asset?: string;
  text?: string;
  scene_index?: number;
  source_scene_index?: number;
  shot_type?: string;
  transition_out?: { type: string; duration_frames: number; overlap_frames: number };
  volume?: number;
  trim_start?: number;
  fade_in?: number;
  fade_out?: number;
  loop?: boolean;
  pan?: number;
}

export interface EditTimelineTrack {
  id: string;
  type: "video" | "audio" | "subtitle";
  role?: "narration" | "music" | "sound_effect";
  clips: EditTimelineClip[];
}

export interface EditTimeline {
  version: string;
  timebase: "frames";
  fps: number;
  width: number;
  height: number;
  duration_frames: number;
  duration_seconds: number;
  tracks: EditTimelineTrack[];
}

export interface StudioAudioAsset {
  asset: string;
  name: string;
  folder: string;
  size_bytes: number;
}

export interface SceneContinuityReport {
  status: string;
  checked_scenes: number;
  method: string;
  warnings: { type: string; scene_indices: number[]; severity: string; message: string; character_id?: string; variants?: { description: string; scene_numbers: number[] }[] }[];
  limitations: string[];
}

export interface SceneVisualDirection {
  scene_index: number;
  storyboard_scene_id?: string;
  narration: string;
  visual_prompt: string;
  visual_prompt_full?: string;
  visual_prompt_suggestion: string;
  negative_prompt?: string;
  continuity?: {
    characters?: string[];
    objects?: string[];
    environment?: string;
    costume?: string;
    time_of_day?: string;
  };
  storyboard_status?: "ready" | "needs_review" | string;
  visual_direction: string;
  narrative_beat: string;
  shot_type: string;
  image_url?: string | null;
  image_status: string;
}

export interface SceneImageAsset {
  scene_index: number;
  image_path?: string;
  image_url?: string;
  provider?: string;
  status: "generated" | "edited" | "fallback" | "candidate";
  candidate_id?: string;
  approval_required?: boolean;
  operation?: "text_to_image" | "image_to_image" | "manual_upload";
  seed?: number;
  prompt?: string;
  visual_prompt?: string;
  narration_text?: string;
  reason?: string;
}

export interface SceneImageCandidate {
  candidate_id: string;
  scene_index: number;
  image_url?: string | null;
  provider?: string;
  operation?: "text_to_image" | "image_to_image";
  prompt?: string;
  negative_prompt?: string;
  seed?: number;
  status: string;
  metadata_match_score?: number;
  metadata_match_terms?: string[];
}

export interface SceneImageFraming { scale: number; offset_x: number; offset_y: number; }

export interface SceneImageHistoryEntry {
  history_id: string;
  scene_index: number;
  image_url?: string | null;
  available: boolean;
  provider?: string;
  operation?: string;
  prompt?: string;
  reason?: string;
  created_at?: number;
}

export interface SceneVideoClip {
  scene_index: number;
  duration: number;
  fps: number;
  width: number;
  height: number;
  output_path?: string;
  output_url?: string;
  bytes?: number;
  encode_engine?: string;
  visual_prompt?: string;
  narration_text?: string;
  audio_status?: "per_scene_narration_muxed" | "no_scene_narration" | "narration_mux_failed" | "single_track_not_split" | "silent_or_tts_unavailable";
  audio_error?: string;
  status?: "updated" | "stale";
  generative_video_path?: string;
  generative_video_url?: string;
  generative_video_provider?: string;
  generative_video_prompt?: string;
  generative_video_duration?: number;
  generative_video_frames?: number;
  generative_video_fps?: number;
  generative_video_status?: "ready" | "failed";
  reason?: string;
}

export interface VidGridRecoveryPlan {
  job_id: string;
  scene_count: number;
  ready_count: number;
  repairable_count: number;
  blocked_count: number;
  repair_scene_indices: number[];
  full_mp4_render_required: boolean;
  scenes: { scene_index: number; status: "ready" | "needs_rebuild"; reasons: string[]; warnings: string[]; clip_exists: boolean; source_image_fingerprint?: string | null }[];
}

export interface VidGridClipRebuildResult {
  job_id: string;
  status: "completed" | "partial" | "failed" | "unchanged" | string;
  requested?: number;
  rebuilt: number;
  failed: number;
  results: { scene_index: number; status: "completed" | "failed" | string; output_url?: string; audio_status?: string; error?: string }[];
  full_mp4_render_required?: boolean;
  message?: string;
  queue?: {
    queue_id?: string;
    requested_scene_indices: number[];
    total: number;
    completed: number;
    failed: number;
    current_scene_index: number | null;
    status: string;
    cancel_requested?: boolean;
    error?: string;
    results: { scene_index: number; status: string; error?: string }[];
    started_at: number;
    updated_at: number;
  };
}

export interface SceneImageSimilarityReport {
  job_id: string;
  status: "duplicates_found" | "no_duplicates_detected";
  method: string;
  threshold_hamming_distance: number;
  image_count: number;
  compared_pairs: number;
  duplicate_pairs: { scene_indices: number[]; match_type: "exact" | "perceptual_near_duplicate"; hamming_distance: number; similarity_percent: number }[];
  skipped_images: { scene_index: number; reason: string }[];
  limitations: string[];
}

export interface StudioJob {
  job_id: string;
  project_id?: string;
  status: string;
  progress: number;
  current_step?: string | null;
  output_url?: string | null;
  output_path?: string | null;
  scene_image_mode?: string | null;
  scene_assets?: SceneImageAsset[] | null;
  scene_image_candidates?: Record<string, (SceneImageAsset & { candidate_id: string })[]> | null;
  storyboard_report?: {
    scene_count: number;
    ready_count: number;
    needs_review_count: number;
    repeated_visuals: { scene_indices: number[]; prompt: string }[];
    warnings: string[];
    historical_fact_policy?: string | null;
  } | null;
  scene_clips?: SceneVideoClip[] | null;
  vidgrid_compatible?: boolean | null;
  clip_duration_seconds?: number | null;
  file_size_bytes?: number | null;
  output_validation?: VideoOutputValidation | null;
  failure_info?: {
    kind?: string;
    failed_stage?: string;
    failed_scene_index?: number | null;
    completed_scene_indices?: number[];
    preserved_image_count?: number;
    preserved_clip_count?: number;
    preserved_narration_count?: number;
    recoverable_scene_indices?: number[];
    automatic_resume_supported?: boolean;
    recovery_hint?: string;
  } | null;
  scene_progress?: {
  scene_clip_rebuild_queue?: VidGridClipRebuildResult["queue"] & { recovery_note?: string };
    scene_index: number;
    status: "pending" | "processing" | "completed" | "fallback" | "failed" | string;
    stage?: string;
    title?: string;
    visual_prompt?: string;
    image_provider?: string;
    image_seed?: number;
    error?: string;
    updated_at?: number;
  }[] | null;
  video_duration?: number | null;
  resolution?: string | null;
  frame_rate?: number | null;
  frames_rendered?: number | null;
  total_frames?: number | null;
  format?: string | null;
  params?: {
    format?: string;
    prompt?: string;
    style?: string;
    duration_seconds?: number;
    resolution?: string;
    frame_rate?: number;
    num_scenes?: number;
    voiceover?: boolean;
    voice_id?: string;
    voice_language?: string;
    voice_speed?: number;
    voice_pitch?: number;
    voiceover_mode?: string;
    generate_subtitles?: boolean;
    character_ids?: string[];
    object_ids?: string[];
    scene_image_mode?: "procedural" | "ai" | "auto";
    scene_image_steps?: number;
    scene_image_seed?: number | null;
    scene_image_timeout?: number;
    vidgrid_compatible?: boolean;
    llm_timeout?: number;
  } | null;
  ai_planner?: string | null;
  edit_timeline?: EditTimeline | null;
  edit_draft_status?: string | null;
  audio_draft_status?: string | null;
  audio_analysis?: {
    sources_analyzed?: number;
    reports?: Record<string, { source?: string; file?: string; rms_dbfs?: number; peak_dbfs?: number; warnings?: string[] }[]>;
    warnings?: { role: string; source: string; code: string }[];
    ducking_recommendation?: { available: boolean; recommended_ducking_db?: number; recommended_threshold_db?: number; reason?: string };
  } | null;
  image_similarity_analysis?: SceneImageSimilarityReport | null;
  mp4_visual_analysis?: {
    status: string;
    sample_count: number;
    comparison_count: number;
    duplicate_pair_count: number;
    low_change_pair_count: number;
    static_runs: { start_seconds: number; end_seconds: number; comparison_count: number }[];
    scene_summaries: { scene_index: number; start_seconds: number; end_seconds: number; sampled_comparisons: number; mean_pixel_change: number | null; repeated_frame_pairs: number; low_change_pairs: number }[];
    comparisons: { from_seconds: number; to_seconds: number; mean_pixel_change: number; perceptual_hash_distance: number; color_histogram_similarity: number; composition_grid_change: number; repeated_frame: boolean; low_visual_change: boolean }[];
    warnings: { code: string; count: number }[];
    analysis_method: string;
    limitations: string[];
    video_duration_seconds: number;
    sample_interval_seconds: number;
    video_source: "original" | "edited";
  } | null;
  visual_intelligence?: {
    studio_id: "whymentary" | "historical_documentary" | "felt_clay";
    status: "good" | "needs_review" | "blocked";
    score: number;
    score_label: string;
    components: { motion: number; composition: number; variety: number; clarity: number };
    scene_count: number;
    moving_camera_scenes: number;
    animated_primitives: number;
    unique_shot_types: number;
    shot_counts: Record<string, number>;
    transition_counts: Record<string, number>;
    character_continuity_changes: number;
    scenes: { scene_index: number; shot_type: string; camera_motion: boolean; animated_primitive_count: number; primitive_count: number; character_ids: string[] }[];
    warnings: { code: string; severity: string; scene_index?: number; [key: string]: unknown }[];
    analysis_method: string;
    limitations: string[];
  } | null;
  av_sync_analysis?: {
    status: "passed" | "needs_review" | "blocked" | "no_narration";
    fps: number;
    video_duration_seconds: number;
    video_scene_count: number;
    narration_clip_count: number;
    scene_comparisons: { scene_index: number; start_delta_ms: number; end_delta_ms: number; aligned: boolean }[];
    warnings: { code: string; severity: string; [key: string]: unknown }[];
    export_blocked: boolean;
    analysis_method: string;
    limitations: string[];
  } | null;
  audio_settings?: { ducking_enabled?: boolean; ducking_db?: number; ducking_threshold_db?: number; ducking_attack?: number; ducking_release?: number; normalization_enabled?: boolean; normalization_target_dbfs?: number; normalization_max_gain_db?: number; loudness_normalization_enabled?: boolean; target_lufs?: number; compressor_enabled?: boolean; compressor_threshold_db?: number; compressor_ratio?: number; compressor_attack?: number; compressor_release?: number; compressor_makeup_db?: number; eq_enabled?: boolean; eq_low_db?: number; eq_mid_db?: number; eq_high_db?: number; mastering_preset?: "custom" | "voice" | "documentary" | "music" | "cinematic_sfx" } | null;
  edit_render_ducking?: { enabled?: boolean; reduction_db?: number; threshold_db?: number; speech_detected?: boolean } | null;
  edit_render_normalization?: { enabled?: boolean; target_dbfs?: number; gain_db?: number; pre_rms?: number } | null;
  edit_render_loudness?: { enabled?: boolean; target_lufs?: number; true_peak_db?: number; input_i?: number; input_tp?: number; input_lra?: number; output_i?: number; output_tp?: number; output_lra?: number; normalization_pass_i?: number; passes?: number; verified?: boolean } | null;
  edit_render_quality?: {
    status?: "passed" | "needs_review" | "blocked";
    export_allowed?: boolean;
    duration_seconds?: number;
    peak_dbfs?: number;
    pre_limiter_peak_dbfs?: number;
    rms_dbfs?: number;
    clipping_ratio?: number;
    silence_gaps?: { start: number; end: number; duration: number }[];
    narration_music_masking?: { start: number; end: number; duration: number; voice_music_gap_db: number }[];
    masking_method?: string;
    warnings?: { code: string; severity: "warning" | "critical"; message: string }[];
    recommendations?: { action: string; recommended_ducking_db?: number; recommended_reduction_db?: number; message: string }[];
    critical_count?: number;
    warning_count?: number;
  } | null;
  edit_render_status?: string | null;
  edit_render_recovery?: {
    kind?: string;
    can_retry_export?: boolean;
    scene_assets_preserved?: boolean;
    scene_records_preserved?: boolean;
    automatic_resume_supported?: boolean;
    message?: string;
  } | null;
  edit_render_transition_policy?: { mode?: string; transitions_applied?: { scene_index: number; type: string; duration_frames: number }[]; message?: string } | null;
  edit_preview_url?: string | null;
  edit_preview_duration?: number | null;
  edit_preview_width?: number | null;
  edit_preview_height?: number | null;
  edit_preview_fps?: number | null;
  edited_output_url?: string | null;
  edited_video_duration?: number | null;
  edit_render_audio?: string | null;
  subtitles?: { format?: string; file_path?: string; download_url?: string | null; cue_count?: number; duration?: number; generated?: boolean; reason?: string } | null;
  voiceover?: {
    muxed?: boolean;
    narration_style?: string;
    clips?: { index: number; start: number; end: number; text: string }[];
    narration?: string;
  } | null;
  error?: string | null;
}

export interface GenerateVideoParams {
  project_id: string;
  prompt: string;
  style?: string;
  duration_seconds?: number;
  resolution?: string;
  frame_rate?: number;
  num_scenes?: number;
  voiceover?: boolean;
  voice_id?: string;
  voice_language?: string;
  voice_speed?: number;
  voice_pitch?: number;
  voiceover_mode?: "per_scene" | "single";
  generate_subtitles?: boolean;
  character_ids?: string[];
  object_ids?: string[];
  llm_timeout?: number;
  format?: string;
  studio_id?: StudioProfile["id"];
  scene_image_mode?: "procedural" | "ai" | "auto";
  scene_image_steps?: number;
  scene_image_seed?: number;
  scene_image_timeout?: number;
  vidgrid_compatible?: boolean;
}

export interface DarkstudioDependencyGraph {
  job_id: string;
  nodes: { id: string; type: string; label: string; status: string; reason?: string | null;
    scene_index?: number | null; bytes?: number | null; probe_status?: string | null; sha256?: string | null }[];
  edges: { from: string; to: string; relationship: string }[];
  summary: { nodes: number; dependencies: number; statuses: Record<string, number> };
  impact_rules: { changed: string; rebuild: string[]; condition?: string }[];
  limitations: string[];
}

export interface DarkstudioDependencyImpact {
  job_id: string;
  changed_asset_ids: string[];
  affected_node_ids: string[];
  affected_nodes: DarkstudioDependencyGraph["nodes"];
  rebuild_scene_indices: number[];
  final_export_required: boolean;
  rebuild_steps: { operation: string; scene_indices?: number[]; reason: string }[];
  requires_user_confirmation: boolean;
  executed: boolean;
  limitations: string[];
}

export interface DarkstudioAssetHealth {
  job_id: string;
  status: "healthy" | "needs_attention";
  summary: { total_assets: number; available: number; missing: number; corrupt: number; unreadable: number; stale?: number };
  scenes: { scene_index?: number; asset_index?: number; group?: string; status: string;
    assets: { kind: string; status: string; reason?: string; bytes?: number; sha256?: string }[] }[];
  checked_at: number;
  limitations: string[];
}

export interface VideoOutputValidation {
  job_id: string;
  path_exists: boolean;
  file_size_bytes: number;
  ffprobe_available: boolean;
  valid: boolean;
  duration_seconds?: number;
  expected_duration_seconds?: number;
  duration_tolerance_seconds?: number;
  format_name?: string;
  video_streams?: number;
  audio_streams?: number;
  video?: { width?: number; height?: number; codec_name?: string; avg_frame_rate?: string; r_frame_rate?: string; pix_fmt?: string } | null;
  audio?: { codec_name?: string; sample_rate?: string; channels?: number } | null;
  resolution?: string;
  fps?: string;
  video_codec?: string;
  pixel_format?: string;
  integrity?: "passed" | "failed" | "not_verified" | "not_checked";
  assembly_mode?: string;
  source_scene_indices?: number[];
  fallback_reason?: string | null;
  subtitle_status?: string;
  subtitle_file_exists?: boolean;
  errors: string[];
  warnings: string[];
}

export interface VideoPreflight {
  status: "ready" | "ready_with_warnings" | "blocked";
  can_queue: boolean;
  project_id: string;
  studio_id: StudioProfile["id"];
  scene_count: number;
  duration_seconds: number;
  clip_duration_seconds: number | null;
  total_frames: number;
  resolution: string;
  fps: number;
  vidgrid_compatible: boolean;
  checks: { id: string; status: string; message: string }[];
  blockers: { id: string; status: string; message: string }[];
  warnings: string[];
  limitations: string[];
}

export const videoStudioApi = {
  async listStudios(): Promise<StudioProfile[]> {
    const { data } = await apiClient.get(`${STUDIO_BASE}/studios`);
    return data?.studios ?? [];
  },

  async getStudio(studioId: StudioProfile["id"]): Promise<StudioProfile> {
    const { data } = await apiClient.get(`${STUDIO_BASE}/studios/${studioId}`);
    return data;
  },

  async listCharacters(studioId: StudioProfile["id"]): Promise<StudioCharacter[]> {
    const { data } = await apiClient.get(`${STUDIO_BASE}/studios/library/characters`, {
      params: { studio_id: studioId },
    });
    return data?.characters ?? [];
  },

  async listSceneObjects(studioId: StudioProfile["id"]): Promise<StudioSceneObject[]> {
    const { data } = await apiClient.get(`${STUDIO_BASE}/studios/library/objects`, {
      params: { studio_id: studioId },
    });
    return data?.objects ?? [];
  },

  async health(): Promise<StudioHealth> {
    const { data } = await apiClient.get(`${STUDIO_BASE}/health`);
    return data;
  },

  async listVoices(): Promise<StudioVoice[]> {
    const { data } = await apiClient.get(`${STUDIO_BASE}/audio/voices`);
    return data?.data?.voices ?? [];
  },

  async getJobVisualDirection(jobId: string): Promise<{
    job_id: string; studio_id: StudioProfile["id"]; scene_count: number; scenes: SceneVisualDirection[];
    storyboard_report?: { continuity_report?: SceneContinuityReport };
  }> {
    const { data } = await apiClient.get(
      `${STUDIO_BASE}/videos/jobs/${jobId}/visual-direction`,
    );
    return data;
  },

  async listSceneImageCandidates(jobId: string, sceneIndex: number): Promise<{
    job_id: string; scene_index: number; candidate_count: number;
    candidates: SceneImageCandidate[]; ranking_note: string;
  }> {
    const { data } = await apiClient.get(
      `${STUDIO_BASE}/visual-assets/jobs/${jobId}/scenes/${sceneIndex}/image-candidates`,
    );
    return data;
  },

  async getJobSceneImageFraming(jobId: string): Promise<{ job_id: string; scenes: Record<string, SceneImageFraming> }> {
    const { data } = await apiClient.get(`${STUDIO_BASE}/visual-assets/jobs/${jobId}/image-framing`);
    return data;
  },

  async updateSceneImageFraming(jobId: string, sceneIndex: number, transform: SceneImageFraming): Promise<{ job_id: string; scene_index: number; status: "saved"; background_image_transform: SceneImageFraming; clip_invalidated: boolean; render_started: boolean }> {
    const { data } = await apiClient.put(`${STUDIO_BASE}/visual-assets/jobs/${jobId}/scenes/${sceneIndex}/image-framing`, transform);
    return data;
  },

  async listSceneImageHistory(jobId: string, sceneIndex: number): Promise<{
    job_id: string; scene_index: number; history_count: number; history: SceneImageHistoryEntry[];
  }> {
    const { data } = await apiClient.get(
      `${STUDIO_BASE}/visual-assets/jobs/${jobId}/scenes/${sceneIndex}/image-history`,
    );
    return data;
  },

  async restoreSceneImageHistory(jobId: string, sceneIndex: number, historyId: string): Promise<{
    job_id: string; scene_index: number; status: "restored"; image_url: string;
    render_required: boolean; message: string; history: SceneImageHistoryEntry[];
  }> {
    const { data } = await apiClient.post(
      `${STUDIO_BASE}/visual-assets/jobs/${jobId}/scenes/${sceneIndex}/image-history/${historyId}/restore`,
    );
    return data;
  },

  async regenerateSelectedSceneImages(jobId: string, scenes: {
    scene_index: number;
    prompt: string;
    negative_prompt?: string;
    seed?: number;
  }[]): Promise<{
    job_id: string;
    status: "completed" | "partial" | "failed";
    requested: number;
    succeeded: number;
    failed: number;
    results: { scene_index: number; status: "candidate" | "failed"; error?: string; result?: SceneImageAsset & { image_url?: string; candidate_id?: string; approval_required?: boolean } }[];
    message: string;
  }> {
    const { data } = await apiClient.post(
      `${STUDIO_BASE}/videos/jobs/${jobId}/scenes/regenerate`,
      { scenes },
    );
    return data;
  },

  async discardSceneImageCandidate(jobId: string, sceneIndex: number, candidateId: string): Promise<{ status: "discarded"; active_image_unchanged: boolean }> {
    const { data } = await apiClient.post(STUDIO_BASE + "/videos/jobs/" + jobId + "/scenes/" + sceneIndex + "/image-candidates/" + candidateId + "/discard");
    return data;
  },

  async approveSceneImageCandidate(jobId: string, sceneIndex: number, candidateId: string): Promise<{ job_id: string; scene_index: number; status: "approved"; image_url: string; render_required: boolean; message: string }> {
    const { data } = await apiClient.post(`${STUDIO_BASE}/videos/jobs/${jobId}/scenes/${sceneIndex}/image-candidates/${candidateId}/approve`);
    return data;
  },

  async getVidGridRecoveryPlan(jobId: string): Promise<VidGridRecoveryPlan> {
    const { data } = await apiClient.get(`${STUDIO_BASE}/videos/jobs/${jobId}/recovery-plan`);
    return data;
  },

  async queueStaleVidGridClips(jobId: string, sceneIndices?: number[]): Promise<{
    job_id: string; queue_id?: string; status: string; queued: boolean; requested: number; status_url?: string;
  }> {
    const { data } = await apiClient.post(
      `${STUDIO_BASE}/videos/jobs/${jobId}/scenes/rebuild-stale-clips/queue`,
      sceneIndices ? { scene_indices: sceneIndices } : {},
    );
    return data;
  },

  async resumeVidGridClipRebuild(jobId: string): Promise<{
    job_id: string; queue_id?: string; status: string; queued: boolean; requested: number; status_url?: string;
  }> {
    const { data } = await apiClient.post(
      `${STUDIO_BASE}/videos/jobs/${jobId}/scenes/rebuild-stale-clips/resume`,
    );
    return data;
  },

  async getVidGridClipRebuildStatus(jobId: string): Promise<NonNullable<VidGridClipRebuildResult["queue"]> & { job_id: string; queue_id?: string; cancel_requested?: boolean; error?: string }> {
    const { data } = await apiClient.get(
      `${STUDIO_BASE}/videos/jobs/${jobId}/scenes/rebuild-stale-clips/status`,
    );
    return data;
  },

  async cancelVidGridClipRebuild(jobId: string): Promise<{ job_id: string; status: string; cancel_requested: boolean; message: string }> {
    const { data } = await apiClient.post(
      `${STUDIO_BASE}/videos/jobs/${jobId}/scenes/rebuild-stale-clips/cancel`,
    );
    return data;
  },

  async rebuildStaleVidGridClips(jobId: string, sceneIndices?: number[]): Promise<VidGridClipRebuildResult> {
    const { data } = await apiClient.post(
      `${STUDIO_BASE}/videos/jobs/${jobId}/scenes/rebuild-stale-clips`,
      sceneIndices ? { scene_indices: sceneIndices } : {},
    );
    return data;
  },

  async uploadSceneImageCandidate(jobId: string, sceneIndex: number, file: File): Promise<{
    job_id: string; scene_index: number; candidate_id: string; image_url: string;
    status: "candidate"; approval_required: true; render_required: false; message: string;
  }> {
    const form = new FormData();
    form.append("file", file);
    const { data } = await apiClient.post(
      `${STUDIO_BASE}/videos/jobs/${jobId}/scenes/${sceneIndex}/image-upload`,
      form,
    );
    return data;
  },

  async editSceneImage(jobId: string, sceneIndex: number, payload: {
    prompt: string;
    negative_prompt?: string;
    denoising_strength?: number;
    steps?: number;
    cfg_scale?: number;
    seed?: number;
    stage_only?: boolean;
  }): Promise<SceneImageAsset & {
    candidate_id?: string;
    approval_required?: boolean;
    job_id: string;
    render_required: boolean;
    scene_clip?: SceneVideoClip & { status?: "updated" | "stale"; reason?: string };
  }> {
    const { data } = await apiClient.post(
      `${STUDIO_BASE}/videos/jobs/${jobId}/scenes/${sceneIndex}/image-edit`,
      payload,
    );
    return data;
  },

  async generateJobSceneMotion(jobId: string, sceneIndex: number, payload: {
    motion_prompt: string;
    negative_prompt?: string;
    provider_timeout?: number;
  }): Promise<{
    job_id: string; scene_index: number; status: string; provider?: string;
    duration: number; frames: number; fps: number; output_path: string;
    download_url: string; message: string;
  }> {
    const { data } = await apiClient.post(
      `${STUDIO_BASE}/videos/jobs/${jobId}/scenes/${sceneIndex}/motion`,
      payload,
    );
    return data;
  },

  async generateImageToVideo(payload: {
    image_ref: string;
    duration_seconds: number;
    fps: number;
    width: number;
    height: number;
    motion_provider: "camera" | "comfyui";
    motion_prompt?: string;
    negative_prompt?: string;
  }): Promise<{ success: boolean; data: { output_path: string; output_url?: string; download_url: string; provider?: string; duration: number; fps: number } }> {
    const { data } = await apiClient.post(`${STUDIO_BASE}/videos/image-to-video`, payload);
    return data;
  },

  async preflightVideo(params: GenerateVideoParams): Promise<VideoPreflight> {
    const { data } = await apiClient.post(`${STUDIO_BASE}/videos/preflight`, params);
    return data;
  },

  async generateVideo(params: GenerateVideoParams): Promise<StudioJob> {
    const { data } = await apiClient.post(`${STUDIO_BASE}/videos/generate`, params);
    return data;
  },

  async getJob(jobId: string): Promise<StudioJob> {
    const { data } = await apiClient.get(`${STUDIO_BASE}/videos/jobs/${jobId}`);
    return data;
  },

  async updateJobTimeline(jobId: string, payload: {
    scene_order: number[];
    scene_edits: { scene_index: number; duration_frames: number; transition_type: string; transition_duration_frames?: number }[];
  }): Promise<{ edit_timeline: EditTimeline; edit_draft_status: string; message: string }> {
    const { data } = await apiClient.patch(`${STUDIO_BASE}/videos/jobs/${jobId}/timeline`, payload);
    return data;
  },

  async listJobAudioAssets(jobId: string): Promise<StudioAudioAsset[]> {
    const { data } = await apiClient.get(`${STUDIO_BASE}/videos/jobs/${jobId}/audio-assets`);
    return data?.assets ?? [];
  },

  async analyzeJobAudio(jobId: string): Promise<{
    sources_analyzed: number;
    reports: Record<string, { source: string; file: string; rms_dbfs: number; peak_dbfs: number; silence_ratio: number; clipping_ratio: number; warnings: string[] }[]>;
    warnings: { role: string; source: string; code: string }[];
    skipped: { role: string; reason: string }[];
    ducking_recommendation: { available: boolean; recommended_ducking_db?: number; recommended_threshold_db?: number; narration_median_rms_dbfs?: number; music_median_rms_dbfs?: number; reason: string };
    message: string;
  }> {
    const { data } = await apiClient.post(`${STUDIO_BASE}/videos/jobs/${jobId}/audio-analysis`);
    return data;
  },
  async analyzeJobSceneImageSimilarity(jobId: string, maxHammingDistance = 6): Promise<SceneImageSimilarityReport> {
    const { data } = await apiClient.post(STUDIO_BASE + "/videos/jobs/" + jobId + "/image-similarity-analysis", null, { params: { max_hamming_distance: maxHammingDistance } });
    return data;
  },

  async analyzeJobMp4Visuals(jobId: string, maxFrames = 48): Promise<NonNullable<StudioJob["mp4_visual_analysis"]>> {
    const { data } = await apiClient.post(`${STUDIO_BASE}/videos/jobs/${jobId}/mp4-visual-analysis`, null, { params: { max_frames: maxFrames } });
    return data;
  },
  async analyzeJobVisuals(jobId: string): Promise<NonNullable<StudioJob["visual_intelligence"]>> {
    const { data } = await apiClient.post(`${STUDIO_BASE}/videos/jobs/${jobId}/visual-analysis`);
    return data;
  },
  async analyzeJobAvSync(jobId: string): Promise<NonNullable<StudioJob["av_sync_analysis"]>> {
    const { data } = await apiClient.post(`${STUDIO_BASE}/videos/jobs/${jobId}/av-sync-analysis`);
    return data;
  },
  async updateJobAudio(jobId: string, payload: {
    music_clips: { asset: string; start: number; end: number; trim_start?: number; volume?: number; fade_in?: number; fade_out?: number; loop?: boolean; pan?: number }[];
    sfx_clips: { asset: string; start: number; end: number; trim_start?: number; volume?: number; fade_in?: number; fade_out?: number; pan?: number }[];
    ducking_enabled?: boolean; ducking_db?: number; ducking_threshold_db?: number;
    ducking_attack?: number; ducking_release?: number; normalization_enabled?: boolean; normalization_target_dbfs?: number; normalization_max_gain_db?: number; loudness_normalization_enabled?: boolean; target_lufs?: number; true_peak_db?: number; loudness_range?: number; compressor_enabled?: boolean; compressor_threshold_db?: number; compressor_ratio?: number; compressor_attack?: number; compressor_release?: number; compressor_makeup_db?: number; eq_enabled?: boolean; eq_low_db?: number; eq_mid_db?: number; eq_high_db?: number; mastering_preset?: "custom" | "voice" | "documentary" | "music" | "cinematic_sfx";
  }): Promise<{ edit_timeline: EditTimeline; audio_draft_status: string; message: string }> {
    const { data } = await apiClient.patch(`${STUDIO_BASE}/videos/jobs/${jobId}/audio`, payload);
    return data;
  },

  async previewJobEdits(jobId: string): Promise<{
    status: string;
    preview_url: string;
    width: number;
    height: number;
    fps: number;
    duration: number;
    generated_scene_count: number;
    message: string;
  }> {
    const { data } = await apiClient.post(`${STUDIO_BASE}/videos/jobs/${jobId}/preview`);
    return data;
  },

  async renderJobEdits(jobId: string): Promise<{
    status: string;
    output_url: string;
    video_duration: number;
    file_size_bytes: number;
    audio_status: string;
    generated_scene_count?: number;
    transition_policy?: { mode?: string; flattened_scenes?: number[]; message?: string } | null;
    ducking?: { enabled?: boolean; reduction_db?: number; speech_detected?: boolean } | null;
    normalization?: { enabled?: boolean; target_dbfs?: number; gain_db?: number; pre_rms?: number } | null;
    loudness?: { enabled?: boolean; target_lufs?: number; true_peak_db?: number; input_i?: number; input_tp?: number; input_lra?: number; output_i?: number; output_tp?: number; output_lra?: number; normalization_pass_i?: number; passes?: number; verified?: boolean } | null;
    quality?: {
    status?: "passed" | "needs_review" | "blocked";
    export_allowed?: boolean;
    duration_seconds?: number;
    peak_dbfs?: number;
    pre_limiter_peak_dbfs?: number;
    rms_dbfs?: number;
    clipping_ratio?: number;
    silence_gaps?: { start: number; end: number; duration: number }[];
    narration_music_masking?: { start: number; end: number; duration: number; voice_music_gap_db: number }[];
    masking_method?: string;
    warnings?: { code: string; severity: "warning" | "critical"; message: string }[];
    recommendations?: { action: string; recommended_ducking_db?: number; recommended_reduction_db?: number; message: string }[];
    critical_count?: number;
    warning_count?: number;
  } | null;
    mastering?: { compressor_enabled?: boolean; compressor_threshold_db?: number; compressor_ratio?: number; compressor_attack?: number; compressor_release?: number; compressor_makeup_db?: number; eq_enabled?: boolean; eq_low_db?: number; eq_mid_db?: number; eq_high_db?: number; mastering_preset?: "custom" | "voice" | "documentary" | "music" | "cinematic_sfx" } | null;
    message: string;
  }> {
    const { data } = await apiClient.post(`${STUDIO_BASE}/videos/jobs/${jobId}/render-edits`);
    return data;
  },

  async getJobDependencyGraph(jobId: string): Promise<DarkstudioDependencyGraph> {
    const { data } = await apiClient.get(`${STUDIO_BASE}/videos/jobs/${jobId}/dependency-graph`);
    return data;
  },

  async previewJobDependencyImpact(jobId: string, changedAssetIds: string[]): Promise<DarkstudioDependencyImpact> {
    const { data } = await apiClient.post(
      `${STUDIO_BASE}/videos/jobs/${jobId}/dependency-impact`,
      { changed_asset_ids: changedAssetIds },
    );
    return data;
  },

  async executeJobDependencyRebuild(jobId: string, changedAssetIds: string[]): Promise<{
    job_id: string;
    status: "queued" | "processing" | "completed" | "partial" | "failed" | "unchanged" | string;
    queued?: boolean;
    executed?: boolean;
    status_url?: string;
    scene_indices?: number[];
    previously_completed_scene_indices?: number[];
    attempt?: number;
    impact?: DarkstudioDependencyImpact;
    rebuild?: { status: string; requested: number; rebuilt: number; failed: number; results: Array<{ scene_index: number; status: string }> } | null;
    render?: { output_url?: string; message?: string } | null;
    message?: string;
  }> {
    const { data } = await apiClient.post(
      `${STUDIO_BASE}/videos/jobs/${jobId}/execute-dependency-rebuild`,
      { changed_asset_ids: changedAssetIds, confirmed: true },
    );
    return data;
  },

  async cancelJobDependencyRebuild(jobId: string): Promise<{ job_id: string; status: string; cancel_requested: boolean; message: string }> {
    const { data } = await apiClient.post(
      `${STUDIO_BASE}/videos/jobs/${jobId}/dependency-rebuild/cancel`,
    );
    return data;
  },

  async resumeJobDependencyRebuild(jobId: string): Promise<{
    job_id: string; status: string; queued: boolean; scene_indices: number[];
    previously_completed_scene_indices: number[]; status_url: string; message: string;
  }> {
    const { data } = await apiClient.post(
      `${STUDIO_BASE}/videos/jobs/${jobId}/dependency-rebuild/resume`,
    );
    return data;
  },

  async getJobDependencyRebuildStatus(jobId: string): Promise<{
    job_id: string;
    status: "queued" | "processing" | "completed" | "partial" | "failed" | "interrupted" | "cancelled" | string;
    cancel_requested?: boolean;
    changed_asset_ids?: string[];
    scene_indices?: number[];
    queued_at?: number;
    started_at?: number;
    updated_at?: number;
    render_output_url?: string;
    render_result?: { output_url?: string; message?: string };
    rebuild_result?: { status: string; requested?: number; rebuilt: number; failed: number; results?: Array<{ scene_index: number; status: string }> } | null;
    error?: string;
    final_export_skipped?: boolean;
  }> {
    const { data } = await apiClient.get(
      `${STUDIO_BASE}/videos/jobs/${jobId}/dependency-rebuild/status`,
    );
    return data;
  },

  async getJobAssetHealth(jobId: string): Promise<DarkstudioAssetHealth> {
    const { data } = await apiClient.get(`${STUDIO_BASE}/videos/jobs/${jobId}/asset-health`);
    return data;
  },

  async validateJobOutput(jobId: string): Promise<VideoOutputValidation> {
    const { data } = await apiClient.post(`${STUDIO_BASE}/videos/jobs/${jobId}/validate-output`);
    return data;
  },

  async listJobs(projectId?: string): Promise<StudioJob[]> {
    const { data } = await apiClient.get(`${STUDIO_BASE}/videos/jobs`, {
      params: projectId ? { project_id: projectId } : undefined,
    });
    return data;
  },
};
