import { useState } from 'react';
import { Check } from 'lucide-react';
import { useAppStore } from '@/store';
import { applyTheme, persistTheme, THEME_OPTIONS } from '@/theme';
import { Avatar, Badge, Button, Card, CardBody, CardHeader, Field, Input, ProgressBar, Switch, Tabs } from '@/ui';

const SECTIONS = [
  { id: 'profile', label: 'Profile' },
  { id: 'appearance', label: 'Appearance' },
  { id: 'notifications', label: 'Notifications' },
  { id: 'integrations', label: 'Integrations' },
  { id: 'storage', label: 'Storage' },
];

const INTEGRATIONS = [
  { id: 'youtube', name: 'YouTube', connected: true },
  { id: 'instagram', name: 'Instagram', connected: true },
  { id: 'facebook', name: 'Facebook', connected: false },
  { id: 'tiktok', name: 'TikTok', connected: false },
  { id: 'twitter', name: 'X (Twitter)', connected: false },
  { id: 'twitch', name: 'Twitch', connected: false },
];

export default function Settings() {
  const user = useAppStore((state) => state.user);
  const setUser = useAppStore((state) => state.setUser);
  const theme = useAppStore((state) => state.theme);
  const setTheme = useAppStore((state) => state.setTheme);
  const addNotification = useAppStore((state) => state.addNotification);

  const [section, setSection] = useState('profile');
  const [name, setName] = useState(user?.name ?? '');
  const [email, setEmail] = useState(user?.email ?? '');
  const [notifPrefs, setNotifPrefs] = useState({ renderComplete: true, newComment: true, weeklyDigest: false, productUpdates: false });
  const [integrations, setIntegrations] = useState(INTEGRATIONS);

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold tracking-tight text-content">Settings</h1>
      <p className="-mt-4 mb-6 text-sm text-subtle">Workspace and account preferences</p>
      <Tabs className="mb-6" tabs={SECTIONS} value={section} onChange={setSection} />

      {section === 'profile' ? (
        <Card className="max-w-xl">
          <CardHeader title="Profile" subtitle="How you appear across the workspace" />
          <CardBody className="space-y-4">
            <div className="flex items-center gap-4">
              <Avatar name={name || 'User'} size="lg" />
              <div>
                <p className="font-medium text-content">{name || 'User'}</p>
                <Badge variant="default">{user?.role ?? 'member'}</Badge>
              </div>
            </div>
            <Field label="Name">
              <Input value={name} onChange={(event) => setName(event.target.value)} />
            </Field>
            <Field label="Email">
              <Input type="email" value={email} onChange={(event) => setEmail(event.target.value)} />
            </Field>
            <Button
              onClick={() => {
                if (user) setUser({ ...user, name, email });
                addNotification({ kind: 'success', title: 'Profile updated', body: 'Your changes were saved.' });
              }}
            >
              Save changes
            </Button>
          </CardBody>
        </Card>
      ) : null}

      {section === 'appearance' ? (
        <Card className="max-w-2xl">
          <CardHeader title="Theme" subtitle="Pick a look for the whole workspace" />
          <CardBody>
            <div className="grid gap-3 sm:grid-cols-3">
              {THEME_OPTIONS.map((option) => (
                <button
                  key={option.name}
                  type="button"
                  onClick={() => {
                    setTheme(option.name);
                    applyTheme(option.name);
                    persistTheme(option.name);
                  }}
                  className={`rounded-lg border p-3 text-left transition-colors ${theme === option.name ? 'border-primary ring-2 ring-primary/40' : 'border-border hover:border-primary/50'}`}
                >
                  <div className="flex items-center gap-2">
                    <span className="h-4 w-4 rounded-full" style={{ backgroundColor: 'rgb(var(--color-primary))' }} />
                    <span className="h-4 w-4 rounded-full" style={{ backgroundColor: 'rgb(var(--color-accent))' }} />
                  </div>
                  <p className="mt-2 text-sm font-medium text-content">{option.label}</p>
                  <p className="text-xs text-subtle">{option.dark ? 'Dark' : 'Light'}</p>
                </button>
              ))}
            </div>
          </CardBody>
        </Card>
      ) : null}

      {section === 'notifications' ? (
        <Card className="max-w-xl">
          <CardHeader title="Notifications" subtitle="Choose what you want to hear about" />
          <CardBody className="space-y-4">
            <Switch label="Render complete" checked={notifPrefs.renderComplete} onChange={(value) => setNotifPrefs((p) => ({ ...p, renderComplete: value }))} />
            <Switch label="New comment on your project" checked={notifPrefs.newComment} onChange={(value) => setNotifPrefs((p) => ({ ...p, newComment: value }))} />
            <Switch label="Weekly digest" checked={notifPrefs.weeklyDigest} onChange={(value) => setNotifPrefs((p) => ({ ...p, weeklyDigest: value }))} />
            <Switch label="Product updates" checked={notifPrefs.productUpdates} onChange={(value) => setNotifPrefs((p) => ({ ...p, productUpdates: value }))} />
          </CardBody>
        </Card>
      ) : null}

      {section === 'integrations' ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {integrations.map((integration) => (
            <Card key={integration.id} className="p-4">
              <div className="flex items-center justify-between">
                <p className="font-medium text-content">{integration.name}</p>
                {integration.connected ? <Badge variant="success">Connected</Badge> : null}
              </div>
              <Button
                className="mt-4"
                size="sm"
                variant={integration.connected ? 'ghost' : 'secondary'}
                onClick={() =>
                  setIntegrations((previous) =>
                    previous.map((item) => (item.id === integration.id ? { ...item, connected: !item.connected } : item)),
                  )
                }
              >
                {integration.connected ? 'Disconnect' : 'Connect'}
              </Button>
            </Card>
          ))}
        </div>
      ) : null}

      {section === 'storage' ? (
        <Card className="max-w-xl">
          <CardHeader title="Storage" subtitle="Workspace media usage" />
          <CardBody>
            <ProgressBar className="mb-2" value={82} variant="accent" />
            <p className="text-sm text-content">82 GB of 100 GB used</p>
            <p className="mt-1 text-xs text-subtle">Enterprise plan — expand to 1 TB anytime</p>
            <Button className="mt-4" variant="secondary">
              <Check className="h-4 w-4" /> Manage plan
            </Button>
          </CardBody>
        </Card>
      ) : null}
    </div>
  );
}
