import "@testing-library/jest-dom/vitest";

// Mock Next.js router
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
  }),
  usePathname: () => "/",
  useSearchParams: () => new URLSearchParams(),
}));

// Mock next-themes
vi.mock("next-themes", () => ({
  useTheme: () => ({
    theme: "light",
    setTheme: vi.fn(),
    resolvedTheme: "light",
  }),
  ThemeProvider: ({ children }: { children: React.ReactNode }) => children,
}));

// Mock zustand store with a functional fake that supports BOTH the selector
// call pattern (components: useAuthStore((s) => s.user)) and the imperative
// API (api client + api-fetch: getState()/setState()). State is mutated in
// place so vi.spyOn(useAuthStore.getState(), "...") keeps working.
vi.mock("@/stores/authStore", () => {
  const state: Record<string, unknown> = {
    user: null,
    accessToken: null,
    refreshToken: null,
    isAuthenticated: false,
    isLoading: false,
    _hydrated: false,
    error: null,
    setUser: vi.fn(),
    setTokens: vi.fn(),
    setLoading: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
    updateUser: vi.fn(),
  };
  const useAuthStore = (selector?: (s: typeof state) => unknown) =>
    selector ? selector(state) : state;
  useAuthStore.getState = () => state;
  useAuthStore.setState = (partial: Partial<typeof state>) => {
    Object.assign(state, partial);
  };
  useAuthStore.subscribe = vi.fn();
  return { useAuthStore };
});

// NOTE: @/api/client is intentionally NOT mocked here — tests/unit/api.test.ts
// exercises the real client (defaults, interceptors). Component tests that need
// a client stub mock it locally.
