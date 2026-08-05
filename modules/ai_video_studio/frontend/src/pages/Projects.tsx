import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FolderPlus, Play, Search } from 'lucide-react';
import type { Project, ProjectStatus } from '@/types';
import { PROJECT_STATUSES, STATUS_LABELS } from '@/constants';
import { fetchProjects } from '@/api';
import { useDebounce } from '@/hooks';
import { timeAgo } from '@/utils';
import { Badge, Button, Card, EmptyState, Input, SectionHeader, Select } from '@/ui';

const statusVariant: Record<string, 'success' | 'info' | 'warning' | 'neutral' | 'danger'> = {
  published: 'success',
  active: 'info',
  rendering: 'warning',
  draft: 'neutral',
};

export default function Projects() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState<'all' | ProjectStatus>('all');
  const debouncedQuery = useDebounce(query, 250);

  useEffect(() => {
    fetchProjects().then(setProjects);
  }, []);

  const filtered = useMemo(
    () =>
      projects.filter((project) => {
        const matchesStatus = status === 'all' || project.status === status;
        const matchesQuery = project.title.toLowerCase().includes(debouncedQuery.toLowerCase());
        return matchesStatus && matchesQuery;
      }),
    [projects, status, debouncedQuery],
  );

  return (
    <div>
      <SectionHeader
        title="Projects"
        subtitle="Manage your video projects"
        action={
          <Button onClick={() => navigate('/editor')}>
            <FolderPlus className="h-4 w-4" /> New Project
          </Button>
        }
      />

      <div className="mb-6 flex flex-wrap items-center gap-3">
        <div className="relative">
          <Search className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-subtle" />
          <Input className="w-72 pl-9" placeholder="Search projects..." value={query} onChange={(event) => setQuery(event.target.value)} />
        </div>
        <Select className="w-44" value={status} onChange={(event) => setStatus(event.target.value as 'all' | ProjectStatus)}>
          <option value="all">All statuses</option>
          {PROJECT_STATUSES.map((value) => (
            <option key={value} value={value}>
              {STATUS_LABELS[value]}
            </option>
          ))}
        </Select>
      </div>

      {filtered.length === 0 ? (
        <EmptyState icon={FolderPlus} title="No projects found" description="Try a different search or filter, or create a new project." />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {filtered.map((project) => (
            <Card key={project.id} className="cursor-pointer transition-colors hover:border-primary/50" onClick={() => navigate('/editor')}>
              <div className="flex h-40 items-center justify-center rounded-t-xl bg-gradient-to-br from-primary/30 to-accent/30">
                <span className="flex h-12 w-12 items-center justify-center rounded-full bg-surface/80">
                  <Play className="h-5 w-5 text-content" />
                </span>
              </div>
              <div className="p-4">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="truncate font-medium text-content">{project.title}</h3>
                  <Badge variant={statusVariant[project.status]}>{STATUS_LABELS[project.status]}</Badge>
                </div>
                <p className="mt-1 text-xs text-subtle">
                  Updated {timeAgo(project.updatedAt)} · {project.collaborators ?? 0} collaborators
                </p>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
