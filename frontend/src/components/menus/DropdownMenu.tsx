"use client";

import {
  useState,
  useRef,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import { cn } from "@/utils/cn";

interface DropdownItem {
  key: string;
  label: string;
  icon?: ReactNode;
  onClick: () => void;
  disabled?: boolean;
  divider?: boolean;
  variant?: "default" | "danger";
}

interface DropdownMenuProps {
  trigger: ReactNode;
  items: DropdownItem[];
  align?: "start" | "end";
  className?: string;
  menuClassName?: string;
}

export function DropdownMenu({
  trigger,
  items,
  align = "start",
  className,
  menuClassName,
}: DropdownMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const handleClickOutside = useCallback((event: MouseEvent) => {
    if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
      setIsOpen(false);
    }
  }, []);

  useEffect(() => {
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen, handleClickOutside]);

  const handleItemClick = (item: DropdownItem) => {
    if (!item.disabled) {
      item.onClick();
      setIsOpen(false);
    }
  };

  return (
    <div ref={menuRef} className={cn("relative inline-block", className)}>
      <div
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            setIsOpen(!isOpen);
          }
        }}
        role="button"
        tabIndex={0}
        aria-haspopup="true"
        aria-expanded={isOpen}
      >
        {trigger}
      </div>

      {isOpen && (
        <div
          className={cn(
            "absolute z-50 mt-1 min-w-[180px] overflow-hidden rounded-lg border border-surface-200 bg-white py-1 shadow-lg animate-fade-in dark:border-surface-700 dark:bg-surface-900",
            align === "end" ? "right-0" : "left-0",
            menuClassName,
          )}
        >
          {items.map((item, index) => (
            <div key={item.key}>
              {item.divider && index > 0 && (
                <div className="my-1 border-t border-surface-200 dark:border-surface-700" />
              )}
              <button
                onClick={() => handleItemClick(item)}
                disabled={item.disabled}
                className={cn(
                  "flex w-full items-center gap-2 px-3 py-2 text-left text-sm transition-colors",
                  item.variant === "danger"
                    ? "text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950"
                    : "text-surface-700 hover:bg-surface-100 dark:text-surface-300 dark:hover:bg-surface-800",
                  item.disabled && "cursor-not-allowed opacity-50",
                )}
              >
                {item.icon && <span className="text-base">{item.icon}</span>}
                {item.label}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
