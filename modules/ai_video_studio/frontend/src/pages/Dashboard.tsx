import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clapperboard, FolderOpen, Play, Radio, Upload, Users } from 'lucide-react';
import type { Project, RenderJob } from '@/types';
import { fetchProjects, fetchRenderJobs } from '@/api';
import { useAppStore } from '@/store';
import { formatDuration, formatNumber, timeAgo } from '@/utils';
import { Badge, Button, Card, CardBody, CardHeader, ProgressBar, SectionHeader, StatCard } from '@/ui';

const statusVariant: Record<string, 'success' | 'info' | 'warning' | 'neutral' | 'danger'> = {
  published: 'success',
  active: 'info',
  rendering: 'warning',
  draft: 'neutral',
  queued: 'neutral',
  done: 'success',
  failed: 'danger',
};

const ACTIVITY = [
  { id: 'a1', actor: 'Ana Souza', action: 'started rendering', target: 'Product Launch 2026', time: new Date(Date.now() - 4 * 60_000).toISOString() },
  { id: 'a2', actor: 'Bruno Lima', action: 'commented on', target: 'Finance Explainer Series', time: new Date(Date.now() - 32 * 60_000).toISOString() },
  { id: 'a3', actor: 'Carla Mendes', action: 'uploaded assets to', target: 'Brand Story — Agriculture', time: new Date(Date.now() - 3 * 3_600_000).toISOString() },
  { id: 'a4', actor: 'Ana Souza', action: 'published', target: 'Shop Drops', time: new Date(Date.now() - 26 * 3_600_000).toISOString() },
  { id: 'a5', actor: 'Bruno Lima', action: 'invited a collaborator to', target: 'Ecommerce Ads Q3', time: new Date(Date.now() - 2 * 86_400_000).toISOString() },
];

export default function Dashboard() {
  const navigate = useNavigate();
  const user = useAppStore((state) => state.user);
  const setProjects = useAppStore((state) => state.setProjects);
  const [projects, setLocalProjects] = useState<Project[]>([]);
  const [jobs, setJobs] = useState<RenderJob[]>([]);

  useEffect(() => {
    fetchProjects().then((data) => {
      setLocalProjects(data);
      setProjects(data);
    });
    fetchRenderJobs().then(setJobs);
  }, [setProjects]);

  return (
    <div className="space-y-6">
      <SectionHeader
        title={user ? `Welcome back, ${user.name.split(' ')[0]}` : 'Welcome back'}
        subtitle="Here is what is happening across your workspace today."
        action={
          <Button onClick={() => navigate('/editor')}>
            <Clapperboard className="h-4 w-4" /> New Project
          </Button>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Projects" value={projects.length} icon={FolderOpen} />
        <StatCard label="Total views" value={formatNumber(1_240_000)} icon={Play} trend="up" delta="12.4%" />
        <StatCard label="Watch time" value={formatDuration(3_620_000)} icon={Radio} trend="up" delta="8.1%" />
        <StatCard label="Subscribers" value={formatNumber(156_000)} icon={Users} trend="up" delta="3.2%" />
      </div>

      <div className="flex flex-wrap gap-3">
        <Button variant="secondary" onClick={() => navigate('/editor')}>
          <Clapperboard className="h-4 w-4" /> New Project
        </Button>
        <Button variant="secondary" onClick={() => navigate('/assets')}>
          <Upload className="h-4 w-4" /> Import
        </Button>
        <Button variant="secondary" onClick={() => navigate('/marketplace')}>
          <FolderOpen className="h-4 w-4" /> Browse Templates
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Recent projects" subtitle="Continue where you left off" action={<Button variant="ghost" size="sm" onClick={() => navigate('/dashboard/projects')}>View all</Button>} />
          <CardBody className="space-y-3">
            {projects.map((project) => (
              <button
                key={project.id}
                type="button"
                onClick={() => navigate('/editor')}
                className="flex w-full items-center gap-3 rounded-lg border border-border bg-surface p-3 text-left transition-colors hover:border-primary/50"
              >
                <span className="flex h-12 w-16 shrink-0 items-center justify-center rounded-md bg-gradient-to-br from-primary/30 to-accent/30">
                  <Play className="h-4 w-4 text-content" />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-sm font-medium text-content">{project.title}</span>
                  <span className="block text-xs text-subtle">
                    {timeAgo(project.updatedAt)} · {project.collaborators ?? 0} collaborators
                  </span>
                </span>
                <Badge variant={statusVariant[project.status]}>{project.status}</Badge>
              </button>
            ))}
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Render queue" subtitle="Active exports across the team" />
          <CardBody className="space-y-4">
            {jobs.map((job) => (
              <div key={job.id} className="space-y-1.5">
                <div className="flex items-center justify-between gap-2">
                  <span className="truncate text-sm font-medium text-content">{job.title}</span>
                  <Badge variant={statusVariant[job.status]}>{job.status}</Badge>
                </div>
                <ProgressBar value={job.progress} variant={job.status === 'done' ? 'accent' : 'default'} />
                <p className="text-xs text-subtle">
                  {job.resolution} · {job.fps} fps{job.gpu ? ` · ${job.gpu}` : ''}
                </p>
              </div>
            ))}
          </CardBody>
        </Card>
      </div>

      <Card>
        <CardHeader title="Recent activity" />
        <CardBody className="divide-y divide-border">
          {ACTIVITY.map((item) => (
            <div key={item.id} className="flex items-center gap-3 py-3">
              <span className="h-2 w-2 shrink-0 rounded-full bg-primary" />
              <p className="min-w-0 flex-1 truncate text-sm text-content">
                <span className="font-medium">{item.actor}</span> {item.action}{' '}
                <span className="text-primary">{item.target}</span>
              </p>
              <span className="shrink-0 text-xs text-subtle">{timeAgo(item.time)}</span>
            </div>
          ))}
        </CardBody>
      </Card>
    </div>
  );
}
