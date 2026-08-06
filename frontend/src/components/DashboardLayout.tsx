"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/authStore";
import { AuthGuard } from "./AuthGuard";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: "📊" },
  { href: "/video-studio", label: "Video Studio", icon: "🎬" },
  { href: "/architecture-graph", label: "Arquitetura", icon: "🕸️" },
  { href: "/architecture-intelligence", label: "Inteligência", icon: "🧠" },
  { href: "/intelligence", label: "Hub IA", icon: "🧩" },
  { href: "/projects", label: "Projetos", icon: "📁" },
  { href: "/agents", label: "Agentes", icon: "🤖" },
  { href: "/workflows", label: "Workflows", icon: "⚡" },
  { href: "/chat", label: "Chat IA", icon: "💬" },
  { href: "/settings", label: "Configurações", icon: "⚙️" },
];

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <AuthGuard>
      <div className="flex min-h-screen bg-surface-50 dark:bg-surface-950">
        <aside className="fixed left-0 top-0 z-30 flex h-full w-64 flex-col border-r bg-white dark:border-surface-700 dark:bg-surface-900">
          <div className="flex h-16 items-center gap-2 border-b px-6 dark:border-surface-700">
            <span className="text-xl">🚀</span>
            <span className="text-lg font-bold text-primary-600">SuperDev</span>
          </div>
          <nav className="flex-1 space-y-1 p-4">
            {navItems.map((item) => {
              const isActive = pathname === item.href || (pathname && pathname.startsWith(item.href + "/"));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300"
                      : "text-surface-600 hover:bg-surface-100 dark:text-surface-400 dark:hover:bg-surface-800"
                  }`}
                >
                  <span>{item.icon}</span>
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <div className="border-t p-4 dark:border-surface-700">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary-100 text-sm font-semibold text-primary-700">
                {user?.email?.charAt(0).toUpperCase() || "U"}
              </div>
              <div className="flex-1 min-w-0">
                <p className="truncate text-sm font-medium text-surface-900 dark:text-surface-50">
                  {user?.fullName || user?.email}
                </p>
                <p className="truncate text-xs text-surface-500">{user?.email}</p>
              </div>
              <button onClick={handleLogout} className="text-xs text-surface-400 hover:text-red-500" title="Sair">
                Sair
              </button>
            </div>
          </div>
        </aside>
        <main className="ml-64 flex-1 p-8">{children}</main>
      </div>
    </AuthGuard>
  );
}
