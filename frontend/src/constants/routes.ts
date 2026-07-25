export const ROUTES = {
  HOME: "/",
  LOGIN: "/login",
  REGISTER: "/register",
  FORGOT_PASSWORD: "/forgot-password",
  RESET_PASSWORD: "/reset-password",
  DASHBOARD: "/dashboard",
  PROJECTS: "/projects",
  PROJECT_DETAIL: (id: string) => `/projects/${id}`,
  PROJECT_EDIT: (id: string) => `/projects/${id}/edit`,
  WORKSPACE: (id: string) => `/workspace/${id}`,
  SETTINGS: "/settings",
  PROFILE: "/profile",
  USERS: "/admin/users",
  API_KEYS: "/settings/api-keys",
  NOT_FOUND: "/404",
  SERVER_ERROR: "/500",
} as const;

export type RouteKeys = keyof typeof ROUTES;
