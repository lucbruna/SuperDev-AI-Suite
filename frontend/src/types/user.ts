import { User, UserRole } from "./auth";

export interface UserProfile extends User {
  bio?: string;
  location?: string;
  website?: string;
  github?: string;
  twitter?: string;
  company?: string;
  phone?: string;
}

export interface UpdateUserRequest {
  fullName?: string;
  username?: string;
  bio?: string;
  location?: string;
  website?: string;
  avatarUrl?: string;
  phone?: string;
}

export interface UpdatePasswordRequest {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export interface UserPreferences {
  theme: "light" | "dark" | "system";
  fontSize: number;
  tabSize: number;
  fontFamily: string;
  autoSave: boolean;
  autoSaveInterval: number;
  language: string;
  notifications: NotificationPreferences;
}

export interface NotificationPreferences {
  email: boolean;
  push: boolean;
  inApp: boolean;
  projectUpdates: boolean;
  mentions: boolean;
  comments: boolean;
}

export interface UserListParams {
  page?: number;
  limit?: number;
  search?: string;
  role?: UserRole;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
}
