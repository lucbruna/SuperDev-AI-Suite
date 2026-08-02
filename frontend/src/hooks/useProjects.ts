"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { projectsApi } from "@/api/projects";
import type {
  Project,
  CreateProjectRequest,
  UpdateProjectRequest,
  ProjectListParams,
} from "@/types/project";

export function useProjects(params?: ProjectListParams) {
  const queryClient = useQueryClient();

  const {
    data: projectsResponse,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["projects", params],
    queryFn: () => projectsApi.getProjects(params),
  });

  const createProject = useMutation({
    mutationFn: (data: CreateProjectRequest) => projectsApi.createProject(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });

  const updateProject = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateProjectRequest }) =>
      projectsApi.updateProject(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });

  const deleteProject = useMutation({
    mutationFn: (id: string) => projectsApi.deleteProject(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });

  return {
    projects: projectsResponse?.items ?? [],
    pagination: projectsResponse
      ? {
          page: projectsResponse.page,
          limit: projectsResponse.page_size,
          totalItems: projectsResponse.total,
          totalPages: projectsResponse.pages,
          hasNextPage: projectsResponse.has_next,
          hasPrevPage: projectsResponse.has_prev,
        }
      : undefined,
    isLoading,
    error,
    createProject,
    updateProject,
    deleteProject,
  };
}

export function useProject(id: string) {
  return useQuery({
    queryKey: ["project", id],
    queryFn: () => projectsApi.getProject(id),
    enabled: !!id,
  });
}
