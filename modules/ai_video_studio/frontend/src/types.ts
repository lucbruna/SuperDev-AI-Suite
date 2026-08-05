/** Shared domain types for the AI Video Studio frontend. */

export type ThemeName =
  | 'dark-enterprise'
  | 'dark-blue'
  | 'dark-green'
  | 'dark-purple'
  | 'light-enterprise'
  | 'high-contrast';

export type Role = 'owner' | 'admin' | 'editor' | 'viewer';

export type Permission = string;

export interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
  avatarUrl?: string;
  status: 'active' | 'invited' | 'suspended';
  lastActive?: string;
}

export type ProjectStatus = 'draft' | 'active' | 'rendering' | 'published';

export interface Project {
  id: string;
  title: string;
  description?: string;
  status: ProjectStatus;
  updatedAt: string;
  thumbnail?: string;
  ownerId: string;
  collaborators?: number;
}

export type AssetType =
  | 'video'
  | 'image'
  | 'audio'
  | 'voice'
  | 'avatar'
  | 'template'
  | 'effect'
  | 'transition'
  | 'font'
  | 'logo'
  | 'subtitle';

export interface Asset {
  id: string;
  name: string;
  type: AssetType;
  size: number;
  url?: string;
  thumbnail?: string;
  tags?: string[];
  createdAt: string;
}

export type RenderStatus = 'queued' | 'rendering' | 'done' | 'failed';

export interface RenderJob {
  id: string;
  projectId: string;
  title: string;
  status: RenderStatus;
  progress: number;
  resolution: string;
  fps: number;
  startedAt?: string;
  finishedAt?: string;
  gpu?: string;
}

export interface Template {
  id: string;
  name: string;
  category: string;
  description?: string;
  preview?: string;
  downloads: number;
  rating: number;
  price: number;
  featured?: boolean;
}

export interface AnalyticsSummary {
  views: number;
  watchTime: number;
  likes: number;
  comments: number;
  shares: number;
  subscribers: number;
}

export interface Comment {
  id: string;
  projectId: string;
  author: string;
  text: string;
  createdAt: string;
  resolved: boolean;
}

export interface Notification {
  id: string;
  kind: 'info' | 'success' | 'warning' | 'error';
  title: string;
  body?: string;
  read: boolean;
  createdAt: string;
}

export interface VoiceProfile {
  id: string;
  name: string;
  language: string;
  gender: 'male' | 'female' | 'neutral';
  emotion: string;
  sampleUrl?: string;
}

export interface AvatarConfig {
  id: string;
  name: string;
  face?: string;
  hair?: string;
  clothing?: string;
  emotion?: string;
  gesture?: string;
}

export interface NavItem {
  label: string;
  path: string;
}

export interface Collaborator {
  id: string;
  user: User;
  permission: Permission;
  joinedAt: string;
}
