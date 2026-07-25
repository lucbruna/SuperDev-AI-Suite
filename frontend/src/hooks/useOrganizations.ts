"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { organizationsApi } from "@/api/organizations";
import type {
  Organization,
  CreateOrganizationRequest,
  UpdateOrganizationRequest,
  InviteMemberRequest,
  OrganizationMember,
} from "@/types/organization";

export function useOrganizations() {
  const queryClient = useQueryClient();

  const {
    data: orgsResponse,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["organizations"],
    queryFn: () => organizationsApi.getOrganizations(),
  });

  const createOrg = useMutation({
    mutationFn: (data: CreateOrganizationRequest) =>
      organizationsApi.createOrganization(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organizations"] });
    },
  });

  const updateOrg = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateOrganizationRequest }) =>
      organizationsApi.updateOrganization(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organizations"] });
    },
  });

  const deleteOrg = useMutation({
    mutationFn: (id: string) => organizationsApi.deleteOrganization(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organizations"] });
    },
  });

  return {
    orgs: orgsResponse?.data ?? [],
    pagination: orgsResponse?.pagination,
    isLoading,
    error,
    createOrg,
    updateOrg,
    deleteOrg,
  };
}

export function useOrganization(id: string) {
  const queryClient = useQueryClient();

  const orgQuery = useQuery({
    queryKey: ["organization", id],
    queryFn: () => organizationsApi.getOrganization(id),
    enabled: !!id,
  });

  const membersQuery = useQuery({
    queryKey: ["organization-members", id],
    queryFn: () => organizationsApi.getMembers(id),
    enabled: !!id,
  });

  const inviteMember = useMutation({
    mutationFn: (data: InviteMemberRequest) =>
      organizationsApi.inviteMember(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organization-members", id] });
    },
  });

  const removeMember = useMutation({
    mutationFn: (memberId: string) =>
      organizationsApi.removeMember(id, memberId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organization-members", id] });
    },
  });

  return {
    organization: orgQuery.data,
    isLoading: orgQuery.isLoading,
    error: orgQuery.error,
    members: (membersQuery.data as OrganizationMember[]) ?? [],
    membersLoading: membersQuery.isLoading,
    inviteMember,
    removeMember,
  };
}
