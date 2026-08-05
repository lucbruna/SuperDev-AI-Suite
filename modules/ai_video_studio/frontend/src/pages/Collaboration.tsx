import { useEffect, useState } from 'react';
import { Pencil, Trash2, UserPlus } from 'lucide-react';
import type { Collaborator, Role } from '@/types';
import { fetchCollaborators } from '@/api';
import { roleLabel } from '@/permissions';
import { useAppStore } from '@/store';
import { formatDate, timeAgo } from '@/utils';
import { Avatar, Badge, Button, Card, CardBody, CardHeader, Field, IconButton, Input, SectionHeader, Select } from '@/ui';

const PERMISSION_ROWS = [
  { id: 'edit', label: 'Can edit', description: 'Modify timeline, assets and settings', roles: '2 editors' },
  { id: 'comment', label: 'Can comment', description: 'Review and leave feedback only', roles: '5 members' },
  { id: 'view', label: 'Can view', description: 'Read-only access to the project', roles: '8 viewers' },
];

const ACTIVITY = [
  { id: '1', actor: 'Ana Souza', text: 'exported Product Launch 2026', time: new Date(Date.now() - 8 * 60_000).toISOString() },
  { id: '2', actor: 'Bruno Lima', text: 'added a comment to Scene 3', time: new Date(Date.now() - 45 * 60_000).toISOString() },
  { id: '3', actor: 'Carla Mendes', text: 'uploaded 3 new assets', time: new Date(Date.now() - 5 * 3_600_000).toISOString() },
  { id: '4', actor: 'Ana Souza', text: 'invited Diego Rocha', time: new Date(Date.now() - 26 * 3_600_000).toISOString() },
  { id: '5', actor: 'Bruno Lima', text: 'renamed the project timeline', time: new Date(Date.now() - 3 * 86_400_000).toISOString() },
];

export default function Collaboration() {
  const addNotification = useAppStore((state) => state.addNotification);
  const [members, setMembers] = useState<Collaborator[]>([]);
  const [inviteOpen, setInviteOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<Role>('editor');

  useEffect(() => {
    fetchCollaborators().then(setMembers);
  }, []);

  const sendInvite = () => {
    if (!inviteEmail.trim()) return;
    const member: Collaborator = {
      id: `inv_${Date.now()}`,
      user: {
        id: `u_${Date.now()}`,
        name: inviteEmail.split('@')[0],
        email: inviteEmail,
        role: inviteRole,
        status: 'invited',
      },
      permission: inviteRole === 'editor' ? 'project:write' : 'project:read',
      joinedAt: new Date().toISOString(),
    };
    setMembers((previous) => [...previous, member]);
    setInviteEmail('');
    setInviteOpen(false);
    addNotification({ kind: 'info', title: 'Invite sent', body: `${member.user.email} was invited as ${roleLabel(inviteRole)}.` });
  };

  return (
    <div>
      <SectionHeader
        title="Collaboration"
        subtitle="Work together in real time"
        action={
          <Button onClick={() => setInviteOpen((value) => !value)}>
            <UserPlus className="h-4 w-4" /> Invite member
          </Button>
        }
      />

      {inviteOpen ? (
        <Card className="mb-6 max-w-lg">
          <CardHeader title="Invite a member" />
          <CardBody className="space-y-4">
            <Field label="Email">
              <Input type="email" placeholder="teammate@company.app" value={inviteEmail} onChange={(event) => setInviteEmail(event.target.value)} />
            </Field>
            <Field label="Role">
              <Select value={inviteRole} onChange={(event) => setInviteRole(event.target.value as Role)}>
                <option value="editor">Editor</option>
                <option value="viewer">Viewer</option>
              </Select>
            </Field>
            <div className="flex gap-2">
              <Button onClick={sendInvite}>Send invite</Button>
              <Button variant="ghost" onClick={() => setInviteOpen(false)}>Cancel</Button>
            </div>
          </CardBody>
        </Card>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader title="Members" subtitle={`${members.length} on this workspace`} />
          <CardBody className="divide-y divide-border">
            {members.map((member) => (
              <div key={member.id} className="flex items-center gap-3 py-3">
                <Avatar name={member.user.name} size="md" />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-content">{member.user.name}</p>
                  <p className="truncate text-xs text-subtle">{member.user.email}</p>
                </div>
                <Badge variant="neutral">{roleLabel(member.user.role)}</Badge>
                <span className="hidden text-xs text-subtle sm:inline">{member.permission}</span>
                <span className="hidden text-xs text-subtle md:inline">{formatDate(member.joinedAt)}</span>
                <IconButton icon={Pencil} label="Edit" size="sm" />
                <IconButton icon={Trash2} label="Remove" size="sm" />
              </div>
            ))}
          </CardBody>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader title="Permissions" />
            <CardBody className="space-y-4">
              {PERMISSION_ROWS.map((row) => (
                <div key={row.id}>
                  <p className="text-sm font-medium text-content">{row.label}</p>
                  <p className="text-xs text-subtle">{row.description}</p>
                  <div className="mt-1 flex items-center justify-between">
                    <Badge variant="neutral">{row.roles}</Badge>
                    <Button variant="ghost" size="sm">Manage</Button>
                  </div>
                </div>
              ))}
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Recent activity" />
            <CardBody className="divide-y divide-border">
              {ACTIVITY.map((item) => (
                <div key={item.id} className="flex items-start gap-3 py-2.5">
                  <Avatar name={item.actor} size="sm" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm text-content">
                      <span className="font-medium">{item.actor}</span> {item.text}
                    </p>
                    <p className="text-xs text-subtle">{timeAgo(item.time)}</p>
                  </div>
                </div>
              ))}
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
}
