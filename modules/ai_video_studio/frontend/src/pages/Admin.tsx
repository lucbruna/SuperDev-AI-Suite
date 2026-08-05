import { useEffect, useMemo, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Check, Database, Download, Gauge, KeyRound, Minus, Pencil, Plus, RefreshCw, Trash2 } from 'lucide-react';
import type { Role, User } from '@/types';
import { NAV_ADMIN } from '@/constants';
import { fetchUsers } from '@/api';
import { roleLabel } from '@/permissions';
import { useAppStore } from '@/store';
import { cn, formatBytes, formatDate, timeAgo } from '@/utils';
import { Avatar, Badge, Button, Card, CardBody, CardHeader, IconButton, ProgressBar, SectionHeader, Select, StatCard } from '@/ui';

const ROLE_DESCRIPTIONS: Record<Role, string> = {
  owner: 'Full access, billing and ownership',
  admin: 'Manage projects, team and settings',
  editor: 'Create and edit projects',
  viewer: 'Read-only access',
};

const ROLE_PERMISSIONS: Record<Role, string[]> = {
  owner: ['*'],
  admin: ['project:read', 'project:write', 'project:delete', 'render:manage', 'team:manage', 'settings:manage', 'admin:view'],
  editor: ['project:read', 'project:write', 'render:start', 'assets:write', 'analytics:read', 'collaborate'],
  viewer: ['project:read', 'analytics:read'],
};

const PERMISSION_GROUPS = [
  { group: 'Project', perms: ['project:read', 'project:write', 'project:delete'] },
  { group: 'Render', perms: ['render:start', 'render:manage'] },
  { group: 'Assets', perms: ['assets:read', 'assets:write'] },
  { group: 'Team', perms: ['team:manage', 'collaborate'] },
  { group: 'Admin', perms: ['settings:manage', 'admin:view'] },
];

const ROLES: Role[] = ['owner', 'admin', 'editor', 'viewer'];

const AUDIT_LOG = [
  { id: '1', actor: 'Ana Souza', action: 'changed role of bruno@superdev.app', target: 'Team', time: new Date(Date.now() - 12 * 60_000).toISOString() },
  { id: '2', actor: 'System', action: 'completed backup nightly', target: 'Backups', time: new Date(Date.now() - 3 * 3_600_000).toISOString() },
  { id: '3', actor: 'Carla Mendes', action: 'signed in from new device', target: 'Security', time: new Date(Date.now() - 26 * 3_600_000).toISOString() },
  { id: '4', actor: 'Bruno Lima', action: 'published project p2', target: 'Projects', time: new Date(Date.now() - 2 * 86_400_000).toISOString() },
];

const LOG_LINES = [
  { level: 'INFO', time: new Date(Date.now() - 2 * 60_000).toISOString(), message: 'render-worker-03: completed job r2 in 4m 12s' },
  { level: 'WARN', time: new Date(Date.now() - 9 * 60_000).toISOString(), message: 'storage: usage at 82% of quota' },
  { level: 'ERROR', time: new Date(Date.now() - 25 * 60_000).toISOString(), message: 'api: failed to reach publisher webhook (retry 2/5)' },
  { level: 'INFO', time: new Date(Date.now() - 40 * 60_000).toISOString(), message: 'auth: 3 successful logins in the last hour' },
  { level: 'WARN', time: new Date(Date.now() - 2 * 3_600_000).toISOString(), message: 'queue: render backlog above threshold' },
];

const NODES = [
  { name: 'render-01', value: 42 },
  { name: 'render-02', value: 67 },
  { name: 'render-03', value: 12 },
  { name: 'api-01', value: 24 },
];

const LICENSES = [
  { id: '1', plan: 'Enterprise', seats: 12, total: 20, status: 'active', expires: new Date(Date.now() + 200 * 86_400_000).toISOString(), price: 199 },
  { id: '2', plan: 'Add-on: AI voices', seats: 5, total: 5, status: 'active', expires: new Date(Date.now() + 90 * 86_400_000).toISOString(), price: 49 },
  { id: '3', plan: 'Add-on: Render GPU pool', seats: 8, total: 8, status: 'expired', expires: new Date(Date.now() - 5 * 86_400_000).toISOString(), price: 99 },
];

const BACKUPS = [
  { id: '1', name: 'backup-2026-08-04', size: 4_200_000_000, status: 'done', created: new Date(Date.now() - 3 * 3_600_000).toISOString() },
  { id: '2', name: 'backup-2026-08-03', size: 4_100_000_000, status: 'done', created: new Date(Date.now() - 27 * 3_600_000).toISOString() },
  { id: '3', name: 'backup-2026-08-02', size: 3_900_000_000, status: 'running', created: new Date(Date.now() - 51 * 3_600_000).toISOString() },
];

export default function Admin() {
  const { pathname } = useLocation();
  const section = useMemo(() => {
    const match = NAV_ADMIN.find((item) => pathname.startsWith(item.path));
    return match?.path.replace('/admin/', '') ?? 'users';
  }, [pathname]);

  return (
    <div>
      <SectionHeader
        title={NAV_ADMIN.find((item) => item.path === `/admin/${section}`)?.label ?? 'Administration'}
        subtitle="Workspace administration and operations"
        action={<Button variant="secondary" onClick={() => useAppStore.getState().addNotification({ kind: 'success', title: 'Action complete', body: 'Demo action executed.' })}>Run action</Button>}
      />
      {section === 'users' ? <UsersSection /> : null}
      {section === 'roles' ? <RolesSection /> : null}
      {section === 'permissions' ? <PermissionsSection /> : null}
      {section === 'audit' ? <AuditSection /> : null}
      {section === 'logs' ? <LogsSection /> : null}
      {section === 'monitoring' ? <MonitoringSection /> : null}
      {section === 'licenses' ? <LicensesSection /> : null}
      {section === 'backups' ? <BackupsSection /> : null}
    </div>
  );
}

function UsersSection() {
  const [users, setUsers] = useState<User[]>([]);
  useEffect(() => {
    fetchUsers().then(setUsers);
  }, []);

  return (
    <Card>
      <CardHeader title="Users" subtitle="Everyone with access to this workspace" />
      <CardBody className="divide-y divide-border">
        {users.map((user) => (
          <div key={user.id} className="flex flex-wrap items-center gap-3 py-3">
            <Avatar name={user.name} size="md" />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-content">{user.name}</p>
              <p className="truncate text-xs text-subtle">{user.email}</p>
            </div>
            <Select className="w-32" value={user.role} onChange={() => undefined}>
              {ROLES.map((role) => (
                <option key={role} value={role}>{roleLabel(role)}</option>
              ))}
            </Select>
            <Badge variant={user.status === 'active' ? 'success' : user.status === 'invited' ? 'info' : 'danger'}>{user.status}</Badge>
            <span className="hidden text-xs text-subtle lg:inline">{user.lastActive ? `active ${timeAgo(user.lastActive)}` : 'never'}</span>
            <IconButton icon={Pencil} label="Edit" size="sm" />
            <IconButton icon={KeyRound} label="Permissions" size="sm" />
            <IconButton icon={Trash2} label="Remove" size="sm" />
          </div>
        ))}
      </CardBody>
    </Card>
  );
}

function RolesSection() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {ROLES.map((role) => (
        <Card key={role} className="flex flex-col">
          <CardHeader title={roleLabel(role)} />
          <CardBody className="flex flex-1 flex-col">
            <p className="text-sm text-subtle">{ROLE_DESCRIPTIONS[role]}</p>
            <div className="mt-3 flex flex-wrap gap-1">
              {ROLE_PERMISSIONS[role].map((permission) => (
                <Badge key={permission} variant="neutral">{permission}</Badge>
              ))}
            </div>
            <div className="mt-auto pt-4">
              <Badge variant="info">{role === 'owner' ? '1 member' : `${role === 'admin' ? 1 : role === 'editor' ? 2 : 5} members`}</Badge>
            </div>
          </CardBody>
        </Card>
      ))}
    </div>
  );
}

function PermissionsSection() {
  return (
    <Card>
      <CardHeader title="Permission matrix" subtitle="Roles × permission groups" />
      <CardBody className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left">
              <th className="pb-2 pr-4 font-medium text-subtle">Group</th>
              {ROLES.map((role) => (
                <th key={role} className="pb-2 px-2 font-medium text-subtle">{roleLabel(role)}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {PERMISSION_GROUPS.map((group) => (
              <tr key={group.group} className="border-b border-border">
                <td className="py-2 pr-4">
                  <p className="font-medium text-content">{group.group}</p>
                  <p className="text-xs text-subtle">{group.perms.join(', ')}</p>
                </td>
                {ROLES.map((role) => {
                  const granted = role === 'owner' || group.perms.some((p) => ROLE_PERMISSIONS[role].includes(p));
                  return (
                    <td key={role} className="px-2 py-2">
                      {granted ? <Check className="h-4 w-4 text-accent" /> : <Minus className="h-4 w-4 text-subtle" />}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </CardBody>
    </Card>
  );
}

function AuditSection() {
  return (
    <Card>
      <CardHeader title="Audit trail" subtitle="Every sensitive action, recorded" action={<Button variant="ghost" size="sm">Export</Button>} />
      <CardBody className="divide-y divide-border">
        {AUDIT_LOG.map((entry) => (
          <div key={entry.id} className="flex items-center gap-3 py-3">
            <Avatar name={entry.actor} size="sm" />
            <p className="min-w-0 flex-1 truncate text-sm text-content">
              <span className="font-medium">{entry.actor}</span> {entry.action}
              <span className="text-primary"> {entry.target}</span>
            </p>
            <span className="shrink-0 text-xs text-subtle">{timeAgo(entry.time)}</span>
          </div>
        ))}
      </CardBody>
    </Card>
  );
}

function LogsSection() {
  const [level, setLevel] = useState('ALL');
  const lines = LOG_LINES.filter((line) => level === 'ALL' || line.level === level);
  return (
    <Card>
      <CardHeader
        title="System logs"
        subtitle="Streaming logs from services"
        action={
          <Select className="w-32" value={level} onChange={(event) => setLevel(event.target.value)}>
            <option>ALL</option>
            <option>INFO</option>
            <option>WARN</option>
            <option>ERROR</option>
          </Select>
        }
      />
      <CardBody>
        <div className="space-y-1.5 rounded-lg border border-border bg-surface p-4 font-mono text-xs">
          {lines.map((line, index) => (
            <div key={index} className="flex items-center gap-3">
              <Badge variant={line.level === 'ERROR' ? 'danger' : line.level === 'WARN' ? 'warning' : 'info'}>{line.level}</Badge>
              <span className="text-subtle">{new Date(line.time).toISOString()}</span>
              <span className="text-content">{line.message}</span>
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  );
}

function MonitoringSection() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard label="CPU" value="42%" icon={Gauge} />
        <StatCard label="GPU pool" value="67%" icon={Gauge} />
        <StatCard label="Queue" value="3 jobs" icon={Database} />
      </div>
      <Card>
        <CardHeader title="Nodes" action={<Button variant="ghost" size="sm"><RefreshCw className="h-4 w-4" /> Refresh</Button>} />
        <CardBody className="space-y-4">
          {NODES.map((node) => (
            <div key={node.name} className="flex items-center gap-4">
              <span className="w-24 text-sm text-content">{node.name}</span>
              <ProgressBar className="flex-1" value={node.value} />
              <span className="w-10 text-right text-xs text-subtle">{node.value}%</span>
            </div>
          ))}
        </CardBody>
      </Card>
    </div>
  );
}

function LicensesSection() {
  return (
    <div className="space-y-4">
      {LICENSES.map((license) => (
        <Card key={license.id} className="p-4">
          <div className="flex flex-wrap items-center gap-3">
            <div className="min-w-0 flex-1">
              <p className="font-medium text-content">{license.plan}</p>
              <p className="text-xs text-subtle">
                {license.seats}/{license.total} seats · renews {formatDate(license.expires)} · ${license.price}/mo
              </p>
            </div>
            <Badge variant={license.status === 'active' ? 'success' : 'danger'}>{license.status}</Badge>
            <Button size="sm" variant="secondary"><Plus className="h-4 w-4" /> Add seats</Button>
          </div>
        </Card>
      ))}
    </div>
  );
}

function BackupsSection() {
  const addNotification = useAppStore((state) => state.addNotification);
  return (
    <Card>
      <CardHeader
        title="Backups"
        subtitle="Nightly snapshots of workspace data"
        action={
          <Button size="sm" onClick={() => addNotification({ kind: 'info', title: 'Backup started', body: 'A new snapshot is being created.' })}>
            <Plus className="h-4 w-4" /> Create backup
          </Button>
        }
      />
      <CardBody className="divide-y divide-border">
        {BACKUPS.map((backup) => (
          <div key={backup.id} className="flex flex-wrap items-center gap-3 py-3">
            <Database className="h-4 w-4 shrink-0 text-primary" />
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-content">{backup.name}</p>
              <p className="text-xs text-subtle">{formatBytes(backup.size)} · {formatDate(backup.created)}</p>
            </div>
            <Badge variant={backup.status === 'done' ? 'success' : 'info'}>{backup.status}</Badge>
            <IconButton icon={Download} label="Download" size="sm" />
          </div>
        ))}
      </CardBody>
    </Card>
  );
}
