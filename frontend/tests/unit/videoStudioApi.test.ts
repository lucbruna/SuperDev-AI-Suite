import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import MockAdapter from "axios-mock-adapter";
import apiClient from "@/api/client";
import { videoStudioApi } from "@/api/videoStudio";

vi.mock("@/constants/api", () => ({
  API_BASE_URL: "http://localhost:8000/api/v1",
  API_TIMEOUT: 30000,
}));

describe("videoStudioApi", () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(apiClient);
  });

  afterEach(() => {
    mock.restore();
  });

  it("fetches health from the studio backend", async () => {
    mock.onGet("/video-studio/health").reply(200, {
      status: "healthy",
      service: "ai-video-studio",
      version: "1.0.0",
    });
    const health = await videoStudioApi.health();
    expect(health.status).toBe("healthy");
    expect(health.service).toBe("ai-video-studio");
  });

  it("lists voices from the narrator catalog", async () => {
    mock.onGet("/video-studio/audio/voices").reply(200, {
      success: true,
      data: {
        voices: [
          { id: "aria", name: "Aria (en, expressive)", gender: "female", language: "en-US" },
          { id: "francisca", name: "Francisca (pt-BR)", gender: "female", language: "pt-BR" },
        ],
      },
    });
    const voices = await videoStudioApi.listVoices();
    expect(voices).toHaveLength(2);
    expect(voices[0].id).toBe("aria");
  });

  it("returns empty voices list on missing payload", async () => {
    mock.onGet("/video-studio/audio/voices").reply(200, { success: true });
    const voices = await videoStudioApi.listVoices();
    expect(voices).toEqual([]);
  });

  it("generates a video with voiceover params", async () => {
    mock.onPost("/video-studio/videos/generate").reply(202, {
      job_id: "job-123",
      status: "queued",
      estimated_seconds: 12,
      message: "Video generation queued",
    });
    const job = await videoStudioApi.generateVideo({
      project_id: "p1",
      prompt: "sunset over ocean",
      voiceover: true,
      voice_id: "francisca",
      voiceover_mode: "per_scene",
    });
    expect(job.job_id).toBe("job-123");
    expect(job.status).toBe("queued");
    const requestBody = JSON.parse(mock.history.post[0].data as string);
    expect(requestBody.voiceover).toBe(true);
    expect(requestBody.voice_id).toBe("francisca");
    expect(requestBody.voiceover_mode).toBe("per_scene");
  });

  it("fetches a single job status", async () => {
    mock.onGet("/video-studio/videos/jobs/job-123").reply(200, {
      job_id: "job-123",
      status: "completed",
      progress: 1.0,
      output_url: "/api/v1/video-studio/downloads/videos/x.mp4",
      file_size_bytes: 1024,
      voiceover: { muxed: true, narration_style: "per_scene", clips: [] },
    });
    const job = await videoStudioApi.getJob("job-123");
    expect(job.status).toBe("completed");
    expect(job.voiceover?.muxed).toBe(true);
  });

  it("lists jobs with optional project filter", async () => {
    mock.onGet("/video-studio/videos/jobs").reply(200, [{ job_id: "a" }, { job_id: "b" }]);
    const jobs = await videoStudioApi.listJobs("p1");
    expect(jobs).toHaveLength(2);
    expect(mock.history.get[0].params).toEqual({ project_id: "p1" });
  });
});
