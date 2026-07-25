"use client";

import { useMemo, useState } from "react";
import { cn } from "@/utils/cn";
import { Badge } from "@/components/badges/Badge";
import { DropdownMenu } from "@/components/menus/DropdownMenu";
import { MoreHorizontal, Mail, UserMinus, Shield, ArrowUpDown } from "lucide-react";

interface MemberRow {
  id: string;
  name: string;
  email: string;
  avatarUrl?: string;
  role: string;
  status: string;
}

interface MembersTableProps {
  members: MemberRow[];
  currentUserRole?: string;
  onRoleChange?: (memberId: string, role: string) => void;
  onRemove?: (memberId: string) => void;
  loading?: boolean;
  className?: string;
}

const roleVariant: Record<string, "primary" | "info" | "default"> = {
  owner: "primary",
  admin: "info",
  member: "default",
};

const statusVariant: Record<string, "success" | "warning" | "default"> = {
  active: "success",
  invited: "warning",
  pending: "warning",
};

export function MembersTable({
  members,
  currentUserRole,
  onRemove,
  loading = false,
  className,
}: MembersTableProps) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const isOwner = currentUserRole === "owner";
  const isAdmin = currentUserRole === "admin";
  const canManage = isOwner || isAdmin;

  const sortedMembers = useMemo(() => {
    if (!sortKey) return members;
    return [...members].sort((a, b) => {
      const aVal = ((a as unknown) as Record<string, string>)[sortKey]?.toLowerCase() ?? "";
      const bVal = ((b as unknown) as Record<string, string>)[sortKey]?.toLowerCase() ?? "";
      if (aVal < bVal) return sortOrder === "asc" ? -1 : 1;
      if (aVal > bVal) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });
  }, [members, sortKey, sortOrder]);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortOrder("asc");
    }
  };

  if (loading) {
    return (
      <div className={cn("overflow-hidden rounded-xl border border-surface-200 dark:border-surface-700", className)}>
        <table className="min-w-full divide-y divide-surface-200 dark:divide-surface-700">
          <thead className="bg-surface-50 dark:bg-surface-800">
            <tr>
              {["Member", "Email", "Role", "Status", ""].map((h) => (
                <th key={h} className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-surface-500 dark:text-surface-400">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-200 dark:divide-surface-700">
            {Array.from({ length: 4 }).map((_, i) => (
              <tr key={i}>
                {Array.from({ length: 5 }).map((_, j) => (
                  <td key={j} className="px-4 py-3">
                    <div className="h-4 animate-pulse rounded bg-surface-200 dark:bg-surface-700" />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (members.length === 0) {
    return (
      <div className={cn("py-12 text-center", className)}>
        <p className="text-sm text-surface-500 dark:text-surface-400">No members found</p>
      </div>
    );
  }

  return (
    <div className={cn("overflow-hidden rounded-xl border border-surface-200 dark:border-surface-700", className)}>
      <table className="min-w-full divide-y divide-surface-200 dark:divide-surface-700">
        <thead className="bg-surface-50 dark:bg-surface-800">
          <tr>
            <th
              className="cursor-pointer select-none px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-surface-500 hover:text-surface-700 dark:text-surface-400 dark:hover:text-surface-200"
              onClick={() => handleSort("name")}
            >
              <div className="flex items-center gap-1">
                Member
                <ArrowUpDown className="h-3 w-3" />
              </div>
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-surface-500 dark:text-surface-400">
              Email
            </th>
            <th
              className="cursor-pointer select-none px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-surface-500 hover:text-surface-700 dark:text-surface-400 dark:hover:text-surface-200"
              onClick={() => handleSort("role")}
            >
              <div className="flex items-center gap-1">
                Role
                <ArrowUpDown className="h-3 w-3" />
              </div>
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-surface-500 dark:text-surface-400">
              Status
            </th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody className="divide-y divide-surface-200 bg-white dark:divide-surface-700 dark:bg-surface-900">
          {sortedMembers.map((member) => (
            <tr key={member.id} className="transition-colors hover:bg-surface-50 dark:hover:bg-surface-800">
              <td className="whitespace-nowrap px-4 py-3">
                <div className="flex items-center gap-3">
                  {member.avatarUrl ? (
                    <img src={member.avatarUrl} alt="" className="h-8 w-8 rounded-full object-cover" />
                  ) : (
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-50 text-xs font-semibold text-primary-600 dark:bg-primary-950 dark:text-primary-400">
                      {member.name.charAt(0).toUpperCase()}
                    </div>
                  )}
                  <span className="text-sm font-medium text-surface-900 dark:text-surface-50">
                    {member.name}
                  </span>
                </div>
              </td>
              <td className="whitespace-nowrap px-4 py-3 text-sm text-surface-500 dark:text-surface-400">
                {member.email}
              </td>
              <td className="whitespace-nowrap px-4 py-3">
                <Badge variant={roleVariant[member.role] ?? "default"} size="sm">
                  {member.role}
                </Badge>
              </td>
              <td className="whitespace-nowrap px-4 py-3">
                <Badge variant={statusVariant[member.status] ?? "default"} size="sm" dot>
                  {member.status}
                </Badge>
              </td>
              <td className="whitespace-nowrap px-4 py-3 text-right">
                {canManage && member.role !== "owner" && (
                  <DropdownMenu
                    align="end"
                    trigger={
                      <button
                        className="rounded-lg p-1.5 text-surface-400 hover:bg-surface-100 hover:text-surface-600 dark:hover:bg-surface-800 dark:hover:text-surface-300"
                        aria-label="Actions"
                      >
                        <MoreHorizontal className="h-4 w-4" />
                      </button>
                    }
                    items={[
                      {
                        key: "email",
                        label: "Send email",
                        icon: <Mail className="h-4 w-4" />,
                        onClick: () => window.location.href = `mailto:${member.email}`,
                      },
                      {
                        key: "remove",
                        label: "Remove member",
                        icon: <UserMinus className="h-4 w-4" />,
                        onClick: () => onRemove?.(member.id),
                        variant: "danger",
                      },
                    ]}
                  />
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
