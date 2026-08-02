"use client";

import { useQuery } from "@tanstack/react-query";
import { dashboardApi, type DashboardData } from "@/api/dashboard";

export function useDashboard() {
  const {
    data,
    isLoading,
    error,
    refetch,
    dataUpdatedAt,
  } = useQuery<DashboardData>({
    queryKey: ["dashboard"],
    queryFn: () => dashboardApi.getDashboard(),
    staleTime: 30_000,
    retry: 2,
    refetchOnWindowFocus: true,
  });

  return {
    data,
    isLoading,
    error,
    refetch,
    dataUpdatedAt,
  };
}
