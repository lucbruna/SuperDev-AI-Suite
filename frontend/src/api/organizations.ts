import apiClient from "./client";
import type {
  Organization,
  OrganizationMember,
  CreateOrganizationRequest,
  UpdateOrganizationRequest,
  InviteMemberRequest,
  OrganizationListParams,
} from "@/types/organization";
import type { ApiResponse, PaginatedResponse } from "@/types/api";

const ORGANIZATIONS_BASE = "/organizations";

export const organizationsApi = {
  getOrganizations: async (params?: OrganizationListParams): Promise<PaginatedResponse<Organization>> => {
    const response = await apiClient.get<PaginatedResponse<Organization>>(
      ORGANIZATIONS_BASE,
      { params },
    );
    return response.data;
  },

  getOrganization: async (id: string): Promise<Organization> => {
    const response = await apiClient.get<ApiResponse<Organization>>(
      `${ORGANIZATIONS_BASE}/${id}`,
    );
    return response.data.data;
  },

  createOrganization: async (data: CreateOrganizationRequest): Promise<Organization> => {
    const response = await apiClient.post<ApiResponse<Organization>>(
      ORGANIZATIONS_BASE,
      data,
    );
    return response.data.data;
  },

  updateOrganization: async (id: string, data: UpdateOrganizationRequest): Promise<Organization> => {
    const response = await apiClient.patch<ApiResponse<Organization>>(
      `${ORGANIZATIONS_BASE}/${id}`,
      data,
    );
    return response.data.data;
  },

  deleteOrganization: async (id: string): Promise<void> => {
    await apiClient.delete(`${ORGANIZATIONS_BASE}/${id}`);
  },

  getMembers: async (organizationId: string): Promise<OrganizationMember[]> => {
    const response = await apiClient.get<ApiResponse<OrganizationMember[]>>(
      `${ORGANIZATIONS_BASE}/${organizationId}/members`,
    );
    return response.data.data;
  },

  addMember: async (organizationId: string, userId: string, role: string): Promise<OrganizationMember> => {
    const response = await apiClient.post<ApiResponse<OrganizationMember>>(
      `${ORGANIZATIONS_BASE}/${organizationId}/members`,
      { user_id: userId, role },
    );
    return response.data.data;
  },

  removeMember: async (organizationId: string, memberId: string): Promise<void> => {
    await apiClient.delete(
      `${ORGANIZATIONS_BASE}/${organizationId}/members/${memberId}`,
    );
  },

  inviteMember: async (organizationId: string, data: InviteMemberRequest): Promise<void> => {
    await apiClient.post(
      `${ORGANIZATIONS_BASE}/${organizationId}/invite`,
      data,
    );
  },
};
