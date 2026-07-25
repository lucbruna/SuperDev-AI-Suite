"use client";

import { cn } from "@/utils/cn";
import { Button } from "@/components/buttons/Button";

interface PluginData {
  id: string;
  icon: string;
  name: string;
  author: string;
  description: string;
  version: string;
  rating: number;
  installCount: number;
  installed: boolean;
}

interface PluginCardProps {
  plugin: PluginData;
  onToggleInstall?: (pluginId: string) => void;
  className?: string;
}

function StarRating({ rating }: { rating: number }) {
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => {
        const fill = rating >= star ? "text-amber-400" : rating >= star - 0.5 ? "text-amber-300" : "text-surface-200 dark:text-surface-600";
        return (
          <svg key={star} className={cn("h-3 w-3", fill)} fill="currentColor" viewBox="0 0 20 20">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        );
      })}
    </div>
  );
}

export function PluginCard({ plugin, onToggleInstall, className }: PluginCardProps) {
  const handleClick = () => {
    onToggleInstall?.(plugin.id);
  };

  return (
    <div
      className={cn(
        "group rounded-xl border border-surface-200 bg-white p-4 shadow-sm transition-all hover:shadow-md dark:border-surface-700 dark:bg-surface-900",
        className,
      )}
    >
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-surface-100 text-xl dark:bg-surface-800">
          {plugin.icon}
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="truncate text-sm font-semibold text-surface-900 dark:text-surface-50">
            {plugin.name}
          </h3>
          <p className="text-xs text-surface-500 dark:text-surface-400">
            {plugin.author}
          </p>
        </div>
      </div>

      <p className="mt-2 line-clamp-2 text-xs text-surface-500 dark:text-surface-400">
        {plugin.description}
      </p>

      <div className="mt-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <StarRating rating={plugin.rating} />
          <span className="text-xs text-surface-400">
            ({plugin.installCount.toLocaleString()})
          </span>
        </div>
        <span className="text-xs text-surface-400">v{plugin.version}</span>
      </div>

      <div className="mt-3">
        <Button
          variant={plugin.installed ? "secondary" : "primary"}
          size="sm"
          fullWidth
          onClick={handleClick}
        >
          {plugin.installed ? "Installed" : "Install"}
        </Button>
      </div>
    </div>
  );
}
