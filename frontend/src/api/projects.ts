import apiClient from "./client";
import { API_ENDPOINTS } from "@/constants/api";
import type {
  Project,
  CreateProjectRequest,
  UpdateProjectRequest,
  ProjectListParams,
} from "@/types/project";
import type { ApiResponse, PaginatedResponse } from "@/types/api";

export const projectsApi = {
  getProjects: async (params?: ProjectListParams): Promise<PaginatedResponse<Project>> => {
    const response = await apiClient.get<PaginatedResponse<Project>>(
      API_ENDPOINTS.PROJECTS.BASE,
      { params },
    );
    return response.data;
  },

  getProject: async (id: string): Promise<Project> => {
    const response = await apiClient.get<ApiResponse<Project>>(
      API_ENDPOINTS.PROJECTS.DETAIL(id),
    );
    return response.data.data;
  },

  createProject: async (data: CreateProjectRequest): Promise<Project> => {
    const response = await apiClient.post<ApiResponse<Project>>(
      API_ENDPOINTS.PROJECTS.BASE,
      data,
    );
    return response.data.data;
  },

  updateProject: async (id: string, data: UpdateProjectRequest): Promise<Project> => {
    const response = await apiClient.patch<ApiResponse<Project>>(
      API_ENDPOINTS.PROJECTS.DETAIL(id),
      data,
    );
    return response.data.data;
  },

  deleteProject: async (id: string): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.PROJECTS.DETAIL(id));
  },

  archiveProject: async (id: string): Promise<Project> => {
    const response = await apiClient.post<ApiResponse<Project>>(
      `${API_ENDPOINTS.PROJECTS.DETAIL(id)}/archive`,
    );
    return response.data.data;
  },
};
