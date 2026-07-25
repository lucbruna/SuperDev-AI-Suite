export interface Project {
  id: string;
  name: string;
  description: string;
  slug: string;
  ownerId: string;
  ownerName: string;
  language: string;
  framework?: string;
  visibility: ProjectVisibility;
  status: ProjectStatus;
  repoUrl?: string;
  demoUrl?: string;
  tags: string[];
  members: ProjectMember[];
  stats: ProjectStats;
  createdAt: string;
  updatedAt: string;
}

export enum ProjectVisibility {
  PUBLIC = "public",
  PRIVATE = "private",
  TEAM = "team",
}

export enum ProjectStatus {
  ACTIVE = "active",
  ARCHIVED = "archived",
  DELETED = "deleted",
}

export interface ProjectMember {
  id: string;
  userId: string;
  email: string;
  username: string;
  avatarUrl?: string;
  role: ProjectRole;
  joinedAt: string;
}

export enum ProjectRole {
  OWNER = "owner",
  ADMIN = "admin",
  MEMBER = "member",
  VIEWER = "viewer",
}

export interface ProjectStats {
  files: number;
  commits: number;
  branches: number;
  contributors: number;
  stars: number;
  forks: number;
  openIssues: number;
  lastActivity: string;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
  language: string;
  framework?: string;
  visibility?: ProjectVisibility;
  tags?: string[];
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string;
  language?: string;
  framework?: string;
  visibility?: ProjectVisibility;
  tags?: string[];
}

export interface ProjectListParams {
  page?: number;
  limit?: number;
  search?: string;
  visibility?: ProjectVisibility;
  status?: ProjectStatus;
  language?: string;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
}
