import { useEffect, useState } from 'react';
import { CheckCircle2, Clock, Gauge, Play, PlusCircle, Radio } from 'lucide-react';
import type { RenderJob } from '@/types';
import { fetchRenderJobs } from '@/api';
import { useAppStore } from '@/store';
import { timeAgo, uid } from '@/utils';
import { Badge, Button, Card, CardBody, CardHeader, EmptyState, Field, ProgressBar, SectionHeader, Select, Spinner, StatCard } from '@/ui';

const statusVariant: Record<string, 'success' | 'info' | 'warning' | 'neutral' | 'danger'> = {
  queued: 'neutral',
  rendering: 'info',
  done: 'success',
  failed: 'danger',
};

export default function RenderCenter() {
  const addNotification = useAppStore((state) => state.addNotification);
  const [jobs, setJobs] = useState<RenderJob[]>([]);
  const [project, setProject] = useState('Product Launch 2026');
  const [resolution, setResolution] = useState('1920x1080');
  const [fps, setFps] = useState(30);
  const [format, setFormat] = useState('MP4');
  const [preset, setPreset] = useState('Balanced');

  useEffect(() => {
    fetchRenderJobs().then(setJobs);
  }, []);

  const startRender = () => {
    const job: RenderJob = {
      id: uid('r'),
      projectId: 'local',
      title: `${project} — ${resolution}`,
      status: 'queued',
      progress: 0,
      resolution,
      fps,
      startedAt: new Date().toISOString(),
      gpu: 'RTX 4090',
    };
    setJobs((previous) => [job, ...previous]);
    addNotification({ kind: 'info', title: 'Render queued', body: 'Your export was added to the queue.' });
  };

  const active = jobs.filter((job) => job.status === 'rendering').length;
  const queued = jobs.filter((job) => job.status === 'queued').length;
  const done = jobs.filter((job) => job.status === 'done').length;

  return (
    <div>
      <SectionHeader title="Render Center" subtitle="Export your projects at production quality" />

      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        <StatCard label="Rendering now" value={active} icon={Gauge} />
        <StatCard label="Queued" value={queued} icon={Clock} />
        <StatCard label="Completed" value={done} icon={CheckCircle2} />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader title="Render jobs" />
            <CardBody className="space-y-4">
              {jobs.length === 0 ? (
                <EmptyState icon={Radio} title="No render jobs" description="Configure a render on the right and hit Start render." />
              ) : (
                jobs.map((job) => (
                  <div key={job.id} className="rounded-lg border border-border bg-surface p-4">
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex min-w-0 items-center gap-2">
                        {job.status === 'rendering' ? <Spinner size="sm" /> : null}
                        <span className="truncate font-medium text-content">{job.title}</span>
                      </div>
                      <Badge variant={statusVariant[job.status]}>{job.status}</Badge>
                    </div>
                    <ProgressBar className="mt-3" value={job.progress} variant={job.status === 'done' ? 'accent' : 'default'} />
                    <p className="mt-2 text-xs text-subtle">
                      {job.resolution} · {job.fps} fps{job.gpu ? ` · ${job.gpu}` : ''}
                      {job.finishedAt ? ` · finished ${timeAgo(job.finishedAt)}` : job.startedAt ? ` · started ${timeAgo(job.startedAt)}` : ''}
                    </p>
                  </div>
                ))
              )}
            </CardBody>
          </Card>
        </div>

        <Card className="self-start">
          <CardHeader title="New render" />
          <CardBody className="space-y-4">
            <Field label="Project">
              <Select value={project} onChange={(event) => setProject(event.target.value)}>
                <option>Product Launch 2026</option>
                <option>Brand Story — Agriculture</option>
                <option>Finance Explainer Series</option>
              </Select>
            </Field>
            <Field label="Resolution">
              <Select value={resolution} onChange={(event) => setResolution(event.target.value)}>
                <option value="1920x1080">1920 × 1080</option>
                <option value="3840x2160">3840 × 2160</option>
                <option value="1280x720">1280 × 720</option>
              </Select>
            </Field>
            <Field label="Frame rate">
              <Select value={String(fps)} onChange={(event) => setFps(Number(event.target.value))}>
                <option value="24">24</option>
                <option value="30">30</option>
                <option value="60">60</option>
              </Select>
            </Field>
            <Field label="Format">
              <Select value={format} onChange={(event) => setFormat(event.target.value)}>
                <option>MP4</option>
                <option>MOV</option>
                <option>WebM</option>
              </Select>
            </Field>
            <Field label="Preset">
              <Select value={preset} onChange={(event) => setPreset(event.target.value)}>
                <option>Quality</option>
                <option>Balanced</option>
                <option>Speed</option>
              </Select>
            </Field>
            <Button className="w-full" onClick={startRender}>
              <Play className="h-4 w-4" /> Start render
            </Button>
            <p className="text-center text-xs text-subtle">GPU pool: RTX 4090 × 8</p>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
