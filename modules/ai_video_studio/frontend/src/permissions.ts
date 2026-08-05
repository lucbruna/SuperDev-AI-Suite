import type { Permission, Role, User } from '@/types';
import { useAppStore } from '@/store';

const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  owner: ['*'],
  admin: [
    'project:read',
    'project:write',
    'project:delete',
    'render:manage',
    'team:manage',
    'settings:manage',
    'admin:view',
    'analytics:read',
    'assets:manage',
    'marketplace:manage',
  ],
  editor: [
    'project:read',
    'project:write',
    'render:start',
    'assets:read',
    'assets:write',
    'analytics:read',
    'collaborate',
  ],
  viewer: ['project:read', 'analytics:read'],
};

export function hasPermission(user: User | null, permission: Permission): boolean {
  if (!user) return false;
  const perms = ROLE_PERMISSIONS[user.role] ?? [];
  return perms.includes('*') || perms.includes(permission);
}

export function can(permission: Permission): boolean {
  return hasPermission(useAppStore.getState().user, permission);
}

export function roleLabel(role: Role): string {
  return role.charAt(0).toUpperCase() + role.slice(1);
}
