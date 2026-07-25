"use client";

import type { Project, ProjectStatus } from "@/types/project";
import { cn } from "@/utils/cn";
import { Badge } from "@/components/badges/Badge";
import { Folder, Clock, Users } from "lucide-react";

interface ProjectCardProps {
  project: Project;
  onClick?: () => void;
  className?: string;
}

const statusVariant: Record<ProjectStatus, "default" | "success" | "warning" | "danger"> = {
  active: "success",
  archived: "warning",
  deleted: "danger",
};

export function ProjectCard({ project, onClick, className }: ProjectCardProps) {
  const lastActivity = project.stats?.lastActivity ?? project.updatedAt;
  const timeAgo = getTimeAgo(lastActivity);

  return (
    <div
      onClick={onClick}
      className={cn(
        "group cursor-pointer rounded-xl border border-surface-200 bg-white p-5 shadow-sm transition-all hover:shadow-md hover:border-primary-300 dark:border-surface-700 dark:bg-surface-900 dark:hover:border-primary-600",
        className,
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-50 text-primary-600 dark:bg-primary-950 dark:text-primary-400">
          <Folder className="h-5 w-5" />
        </div>
        <Badge variant={statusVariant[project.status]} size="sm">
          {project.status}
        </Badge>
      </div>

      <h3 className="mt-4 text-sm font-semibold text-surface-900 dark:text-surface-50 group-hover:text-primary-600 dark:group-hover:text-primary-400">
        {project.name}
      </h3>

      {project.description && (
        <p className="mt-1 line-clamp-2 text-xs text-surface-500 dark:text-surface-400">
          {project.description}
        </p>
      )}

      <div className="mt-3 flex flex-wrap gap-1.5">
        <Badge variant="primary" size="sm">
          {project.language}
        </Badge>
        {project.tags?.slice(0, 3).map((tag) => (
          <Badge key={tag} variant="default" size="sm">
            {tag}
          </Badge>
        ))}
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-surface-100 pt-3 dark:border-surface-800">
        <div className="flex items-center gap-3 text-xs text-surface-500 dark:text-surface-400">
          <span className="flex items-center gap-1">
            <Clock className="h-3.5 w-3.5" />
            {timeAgo}
          </span>
          <span className="flex items-center gap-1">
            <Users className="h-3.5 w-3.5" />
            {project.members?.length ?? 0}
          </span>
        </div>

        {project.members && project.members.length > 0 && (
          <div className="flex -space-x-2">
            {project.members.slice(0, 3).map((member) => (
              <div
                key={member.id}
                className="h-6 w-6 rounded-full border-2 border-white bg-surface-300 text-[10px] font-medium text-surface-600 flex items-center justify-center dark:border-surface-900 dark:bg-surface-700 dark:text-surface-300"
                title={member.username}
              >
                {member.username.charAt(0).toUpperCase()}
              </div>
            ))}
            {project.members.length > 3 && (
              <div className="h-6 w-6 rounded-full border-2 border-white bg-surface-100 text-[10px] font-medium text-surface-500 flex items-center justify-center dark:border-surface-900 dark:bg-surface-800 dark:text-surface-400">
                +{project.members.length - 3}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function getTimeAgo(dateString: string): string {
  const now = Date.now();
  const date = new Date(dateString).getTime();
  const diffMs = now - date;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHr = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHr / 24);

  if (diffSec < 60) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  if (diffDay < 7) return `${diffDay}d ago`;
  return new Date(dateString).toLocaleDateString();
}
