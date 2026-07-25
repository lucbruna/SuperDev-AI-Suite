import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import MockAdapter from "axios-mock-adapter";
import apiClient from "@/api/client";
import { useAuthStore } from "@/stores/authStore";

vi.mock("@/constants/api", () => ({
  API_BASE_URL: "http://localhost:8000/api/v1",
  API_TIMEOUT: 30000,
}));

describe("API Client", () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(apiClient);
    useAuthStore.setState({
      accessToken: null,
      refreshToken: null,
    });
  });

  afterEach(() => {
    mock.restore();
  });

  it("creates axios instance with base URL", () => {
    expect(apiClient.defaults.baseURL).toBe("http://localhost:8000/api/v1");
    expect(apiClient.defaults.timeout).toBe(30000);
  });

  it("creates axios instance with JSON content type", () => {
    expect(apiClient.defaults.headers["Content-Type"]).toBe("application/json");
  });

  it("adds auth header when token exists", async () => {
    useAuthStore.setState({ accessToken: "test-token-123" });
    mock.onGet("/test").reply((config) => {
      expect(config.headers?.Authorization).toBe("Bearer test-token-123");
      return [200, { success: true }];
    });
    const response = await apiClient.get("/test");
    expect(response.status).toBe(200);
  });

  it("does not add auth header when no token", async () => {
    mock.onGet("/test").reply((config) => {
      expect(config.headers?.Authorization).toBeUndefined();
      return [200, { success: true }];
    });
    const response = await apiClient.get("/test");
    expect(response.status).toBe(200);
  });

  it("handles 401 response by attempting token refresh", async () => {
    useAuthStore.setState({
      accessToken: "expired-token",
      refreshToken: "valid-refresh-token",
    });
    const setTokensSpy = vi.spyOn(useAuthStore.getState(), "setTokens");
    const logoutSpy = vi.spyOn(useAuthStore.getState(), "logout");

    mock.onGet("/protected").replyOnce(401);
    mock.onPost("/auth/refresh").replyOnce(200, {
      data: { accessToken: "new-access-token", refreshToken: "new-refresh-token" },
    });

    const response = await apiClient.get("/protected");
    expect(response.status).toBe(200);
  });

  it("calls logout when refresh fails", async () => {
    useAuthStore.setState({
      accessToken: "expired-token",
      refreshToken: "invalid-refresh-token",
    });
    const logoutSpy = vi.spyOn(useAuthStore.getState(), "logout");

    mock.onGet("/protected").replyOnce(401);
    mock.onPost("/auth/refresh").replyOnce(401);

    await expect(apiClient.get("/protected")).rejects.toThrow();
    expect(logoutSpy).toHaveBeenCalled();
  });

  it("calls logout when no refresh token exists", async () => {
    useAuthStore.setState({
      accessToken: "expired-token",
      refreshToken: null,
    });
    const logoutSpy = vi.spyOn(useAuthStore.getState(), "logout");

    mock.onGet("/protected").replyOnce(401);

    await expect(apiClient.get("/protected")).rejects.toThrow();
    expect(logoutSpy).toHaveBeenCalled();
  });

  it("passes through non-401 errors", async () => {
    mock.onGet("/test").replyOnce(500, { message: "Server error" });
    try {
      await apiClient.get("/test");
    } catch (error: unknown) {
      const axiosError = error as { response?: { status: number; data: { message: string } } };
      expect(axiosError.response?.status).toBe(500);
      expect(axiosError.response?.data.message).toBe("Server error");
    }
  });

  it("handles successful response", async () => {
    mock.onGet("/test").replyOnce(200, { data: "ok" });
    const response = await apiClient.get("/test");
    expect(response.data).toEqual({ data: "ok" });
  });
});