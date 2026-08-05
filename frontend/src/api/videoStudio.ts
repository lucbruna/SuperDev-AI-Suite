import apiClient from "./client";

// ---------------------------------------------------------------------------
// AI Video Studio API client — connects the dashboard to the real module
// backend mounted at /api/v1/video-studio (see backend/app.py).
// ---------------------------------------------------------------------------

const STUDIO_BASE = "/video-studio";

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
    llm_timeout?: number;
  } | null;
  ai_planner?: string | null;
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
  llm_timeout?: number;
  format?: string;
}

export const videoStudioApi = {
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

  async listJobs(projectId?: string): Promise<StudioJob[]> {
    const { data } = await apiClient.get(`${STUDIO_BASE}/videos/jobs`, {
      params: projectId ? { project_id: projectId } : undefined,
    });
    return data;
  },
};
