import apiClient from "./client";
import { API_ENDPOINTS } from "@/constants/api";
import type {
  Project,
  CreateProjectRequest,
  UpdateProjectRequest,
  ProjectListParams,
} from "@/types/project";
import type { ApiResponse } from "@/types/api";

export interface ProjectListResponse {
  items: Project[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export const projectsApi = {
  getProjects: async (params?: ProjectListParams): Promise<ProjectListResponse> => {
    const response = await apiClient.get<ProjectListResponse>(
      API_ENDPOINTS.PROJECTS.BASE,
      { params },
    );
    return response.data;
  },

  getProject: async (id: string): Promise<Project> => {
    const response = await apiClient.get<Project>(
      API_ENDPOINTS.PROJECTS.DETAIL(id),
    );
    return response.data;
  },

  createProject: async (data: CreateProjectRequest): Promise<Project> => {
    const response = await apiClient.post<Project>(
      API_ENDPOINTS.PROJECTS.BASE,
      data,
    );
    return response.data;
  },

  updateProject: async (id: string, data: UpdateProjectRequest): Promise<Project> => {
    const response = await apiClient.put<Project>(
      API_ENDPOINTS.PROJECTS.DETAIL(id),
      data,
    );
    return response.data;
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
