import type { User } from "./auth";

export interface Organization {
  id: string;
  name: string;
  slug: string;
  description?: string;
  logo_url?: string;
  website?: string;
  owner_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export enum OrganizationRole {
  OWNER = "owner",
  ADMIN = "admin",
  MEMBER = "member",
}

export interface OrganizationMember {
  id: string;
  organization_id: string;
  user_id: string;
  user: User;
  role: OrganizationRole;
  created_at: string;
}

export interface CreateOrganizationRequest {
  name: string;
  slug?: string;
  description?: string;
  website?: string;
  logo_url?: string;
}

export interface UpdateOrganizationRequest {
  name?: string;
  slug?: string;
  description?: string;
  website?: string;
  logo_url?: string;
}

export interface InviteMemberRequest {
  email: string;
  role: OrganizationRole;
  message?: string;
}

export interface OrganizationListParams {
  page?: number;
  limit?: number;
  search?: string;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
}
