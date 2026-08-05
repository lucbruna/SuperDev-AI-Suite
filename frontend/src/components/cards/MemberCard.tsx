"use client";

import Image from "next/image";
import type { OrganizationMember } from "@/types/organization";
import type { ProjectMember } from "@/types/project";
import { cn } from "@/utils/cn";
import { roleVariant } from "@/utils/format";
import { Badge } from "@/components/badges/Badge";
import { DropdownMenu } from "@/components/menus/DropdownMenu";
import { MoreHorizontal, Mail, UserMinus, Shield } from "lucide-react";

type Member = (OrganizationMember | ProjectMember) & {
  roleDisplay?: string;
};

interface MemberCardProps {
  member: Member;
  currentUserRole?: string;
  onRoleChange?: (memberId: string, role: string) => void;
  onRemove?: (memberId: string) => void;
  className?: string;
}

export function MemberCard({
  member,
  currentUserRole,
  onRemove,
  className,
}: MemberCardProps) {
  const isOwner = currentUserRole === "owner";
  const isAdmin = currentUserRole === "admin";
  const canManage = isOwner || isAdmin;

  const displayName = "user" in member ? member.user.fullName || member.user.username : member.username;
  const displayEmail = "user" in member ? member.user.email : member.email;
  const avatarUrl = "user" in member ? member.user.avatarUrl : member.avatarUrl;
  const avatarInitial = ("user" in member ? member.user.username : member.username).charAt(0).toUpperCase();
  const role = member.role as string;

  return (
    <div
      className={cn(
        "flex items-center gap-4 rounded-xl border border-surface-200 bg-white p-4 shadow-sm dark:border-surface-700 dark:bg-surface-900",
        className,
      )}
    >
      {avatarUrl ? (
        <Image
          src={avatarUrl}
          alt={displayName}
          width={40}
          height={40}
          className="h-10 w-10 rounded-full object-cover"
        />
      ) : (
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-50 text-sm font-semibold text-primary-600 dark:bg-primary-950 dark:text-primary-400">
          {avatarInitial}
        </div>
      )}

      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-surface-900 dark:text-surface-50">
          {displayName}
        </p>
        <p className="truncate text-xs text-surface-500 dark:text-surface-400">
          {displayEmail}
        </p>
      </div>

      <Badge variant={roleVariant(role)} size="sm">
        {role}
      </Badge>

      {canManage && (
        <DropdownMenu
          align="end"
          trigger={
            <button
              className="rounded-lg p-1.5 text-surface-400 hover:bg-surface-100 hover:text-surface-600 dark:hover:bg-surface-800 dark:hover:text-surface-300"
              aria-label="Member actions"
            >
              <MoreHorizontal className="h-4 w-4" />
            </button>
          }
          items={[
            {
              key: "email",
              label: "Send email",
              icon: <Mail className="h-4 w-4" />,
              onClick: () => window.location.href = `mailto:${displayEmail}`,
            },
            ...(role !== "owner"
              ? [
                  {
                    key: "remove",
                    label: "Remove member",
                    icon: <UserMinus className="h-4 w-4" />,
                    onClick: () => onRemove?.(member.id),
                    variant: "danger" as const,
                  },
                ]
              : []),
          ]}
        />
      )}
    </div>
  );
}
