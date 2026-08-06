"use client";

import { useState, type ReactNode } from "react";
import Link from "next/link";
import { cn } from "@/utils/cn";
import { Button } from "@/components/buttons/Button";
import { ROUTES } from "@/constants/routes";

interface MainLayoutProps {
  children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen overflow-hidden">
      <aside
        className={cn(
          "flex flex-col border-r bg-surface-50 dark:bg-surface-900 transition-all duration-300",
          isSidebarOpen ? "w-64" : "w-16",
        )}
      >
        <div className="flex h-14 items-center justify-between border-b px-4">
          {isSidebarOpen && (
            <Link href={ROUTES.DASHBOARD} className="text-lg font-bold text-primary-600">
              SuperDev
            </Link>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            aria-label={isSidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
          >
            {isSidebarOpen ? "◀" : "▶"}
          </Button>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto p-2">
          <SidebarItem
            href={ROUTES.DASHBOARD}
            icon="📊"
            label="Dashboard"
            collapsed={!isSidebarOpen}
          />
          <SidebarItem
            href={ROUTES.PROJECTS}
            icon="📁"
            label="Projects"
            collapsed={!isSidebarOpen}
          />
          <SidebarItem
            href={ROUTES.DIGITAL_TWIN}
            icon="🧬"
            label="Digital Twin"
            collapsed={!isSidebarOpen}
          />
          <SidebarItem
            href={ROUTES.SELF_HEALING}
            icon="🩺"
            label="Self-Healing"
            collapsed={!isSidebarOpen}
          />
          <SidebarItem
            href={ROUTES.AUTONOMOUS_DEVELOPER}
            icon="🤖"
            label="Autonomous Dev"
            collapsed={!isSidebarOpen}
          />
          <SidebarItem
            href={ROUTES.KNOWLEDGE_GRAPH}
            icon="🕸️"
            label="Knowledge Graph"
            collapsed={!isSidebarOpen}
          />
          <SidebarItem
            href={ROUTES.WORKSPACES}
            icon="🗂️"
            label="Workspaces"
            collapsed={!isSidebarOpen}
          />
        </nav>

        <div className="border-t p-2">
          <SidebarItem
            href={ROUTES.SETTINGS}
            icon="⚙️"
            label="Settings"
            collapsed={!isSidebarOpen}
          />
        </div>
      </aside>

      <main className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-14 items-center justify-between border-b bg-white px-6 dark:bg-surface-950">
          <h1 className="text-lg font-semibold text-surface-900 dark:text-surface-100">
            Welcome
          </h1>
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="sm">
              Notifications
            </Button>
            <Button variant="ghost" size="sm">
              Profile
            </Button>
          </div>
        </header>

        <div className="flex-1 overflow-auto p-6">{children}</div>
      </main>
    </div>
  );
}

interface SidebarItemProps {
  href: string;
  icon: string;
  label: string;
  collapsed: boolean;
}

function SidebarItem({ href, icon, label, collapsed }: SidebarItemProps) {
  return (
    <Link
      href={href}
      className={cn(
        "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
        "text-surface-600 hover:bg-surface-100 hover:text-surface-900",
        "dark:text-surface-400 dark:hover:bg-surface-800 dark:hover:text-surface-100",
        collapsed && "justify-center px-2",
      )}
      title={collapsed ? label : undefined}
    >
      <span className="text-lg">{icon}</span>
      {!collapsed && <span>{label}</span>}
    </Link>
  );
}
