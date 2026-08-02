"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/authStore";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, accessToken, _hydrated, logout } = useAuthStore();

  useEffect(() => {
    if (_hydrated && (!isAuthenticated || !accessToken)) {
      if (isAuthenticated && !accessToken) logout();
      router.replace("/login");
    }
  }, [accessToken, isAuthenticated, _hydrated, logout, router]);

  if (!_hydrated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-surface-50 dark:bg-surface-950">
        <div className="text-surface-500">Carregando...</div>
      </div>
    );
  }

  if (!isAuthenticated || !accessToken) {
    return null;
  }

  return <>{children}</>;
}
