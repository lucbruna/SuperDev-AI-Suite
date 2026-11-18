import apiClient from "./client";

// ---------------------------------------------------------------------------
// AI Video Studio API client — connects the dashboard to the real module
// backend mounted at /api/v1/video-studio (see backend/app.py).
// ---------------------------------------------------------------------------

const STUDIO_BASE = "/video-studio";

export interface StudioProfile {
  id: "whymentary" | "historical_documentary";
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

export interface StudioJob {
  job_id: string;
  project_id: string;
  status: string;
  progress: number;
  current_step?: string | null;
  output_url?: string | null;
  output_path?: string | null;
  file_size_bytes?: number | null;
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

  async renderJobEdits(jobId: string): Promise<{
    status: string;
    output_url: string;
    video_duration: number;
    file_size_bytes: number;
    audio_status: string;
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

  async listJobs(projectId?: string): Promise<StudioJob[]> {
    const { data } = await apiClient.get(`${STUDIO_BASE}/videos/jobs`, {
      params: projectId ? { project_id: projectId } : undefined,
    });
    return data;
  },
};
