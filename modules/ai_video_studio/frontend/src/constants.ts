import type { NavItem } from '@/types';

export const APP_NAME = 'SuperDev AI Video Studio';
export const APP_VERSION = '8.0.0';

export const ROUTES = {
  home: '/',
  dashboard: '/dashboard',
  editor: '/editor',
  assets: '/assets',
  marketplace: '/marketplace',
  avatarStudio: '/avatar',
  voiceStudio: '/voice',
  renderCenter: '/render',
  analytics: '/analytics',
  settings: '/settings',
  collaboration: '/collaboration',
  admin: '/admin',
  login: '/login',
} as const;

export const PROJECT_STATUSES = ['draft', 'active', 'rendering', 'published'] as const;
export const RENDER_STATUSES = ['queued', 'rendering', 'done', 'failed'] as const;
export const ASSET_TYPES = [
  'video',
  'image',
  'audio',
  'voice',
  'avatar',
  'template',
  'effect',
  'transition',
  'font',
  'logo',
  'subtitle',
] as const;

export const TEMPLATE_CATEGORIES = [
  'Business',
  'Education',
  'Agriculture',
  'Healthcare',
  'Finance',
  'Tourism',
  'Ecommerce',
  'Social Media',
] as const;

export const STATUS_LABELS: Record<string, string> = {
  draft: 'Draft',
  active: 'Active',
  rendering: 'Rendering',
  published: 'Published',
  queued: 'Queued',
  done: 'Done',
  failed: 'Failed',
};

export const NAV_MAIN: NavItem[] = [
  { label: 'Dashboard', path: '/dashboard' },
  { label: 'Projects', path: '/dashboard/projects' },
  { label: 'Editor', path: '/editor' },
  { label: 'Assets', path: '/assets' },
  { label: 'Marketplace', path: '/marketplace' },
  { label: 'Avatar Studio', path: '/avatar' },
  { label: 'Voice Studio', path: '/voice' },
  { label: 'Render Center', path: '/render' },
  { label: 'Analytics', path: '/analytics' },
  { label: 'Collaboration', path: '/collaboration' },
  { label: 'Settings', path: '/settings' },
];

export const NAV_ADMIN: NavItem[] = [
  { label: 'Users', path: '/admin/users' },
  { label: 'Roles', path: '/admin/roles' },
  { label: 'Permissions', path: '/admin/permissions' },
  { label: 'Audit', path: '/admin/audit' },
  { label: 'Logs', path: '/admin/logs' },
  { label: 'Monitoring', path: '/admin/monitoring' },
  { label: 'Licenses', path: '/admin/licenses' },
  { label: 'Backups', path: '/admin/backups' },
];
