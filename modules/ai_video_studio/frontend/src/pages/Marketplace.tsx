import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LayoutTemplate, Play, Search, Star } from 'lucide-react';
import type { Template } from '@/types';
import { TEMPLATE_CATEGORIES } from '@/constants';
import { fetchTemplates } from '@/api';
import { useDebounce } from '@/hooks';
import { cn, formatNumber } from '@/utils';
import { Badge, Button, Card, EmptyState, Input, SectionHeader } from '@/ui';

export default function Marketplace() {
  const navigate = useNavigate();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('All');
  const debouncedQuery = useDebounce(query, 250);

  useEffect(() => {
    fetchTemplates().then(setTemplates);
  }, []);

  const filtered = useMemo(
    () =>
      templates.filter((template) => {
        const matchesCategory = category === 'All' || template.category === category;
        const matchesQuery = template.name.toLowerCase().includes(debouncedQuery.toLowerCase());
        return matchesCategory && matchesQuery;
      }),
    [templates, category, debouncedQuery],
  );

  const featured = templates.filter((template) => template.featured);

  return (
    <div>
      <SectionHeader title="Marketplace" subtitle="Templates for every industry" />

      <div className="mb-6 flex flex-wrap items-center gap-3">
        <div className="relative">
          <Search className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-subtle" />
          <Input className="w-72 pl-9" placeholder="Search templates..." value={query} onChange={(event) => setQuery(event.target.value)} />
        </div>
        <div className="flex flex-wrap gap-2">
          {['All', ...TEMPLATE_CATEGORIES].map((value) => (
            <button
              key={value}
              type="button"
              onClick={() => setCategory(value)}
              className={cn(
                'rounded-full border px-3 py-1 text-sm transition-colors',
                category === value ? 'border-primary bg-primary text-white' : 'border-border text-subtle hover:text-content',
              )}
            >
              {value}
            </button>
          ))}
        </div>
      </div>

      {featured.length > 0 ? (
        <section className="mb-8">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-subtle">Featured</h2>
          <div className="flex gap-4 overflow-x-auto pb-2">
            {featured.map((template) => (
              <TemplateCard key={template.id} template={template} onUse={() => navigate('/editor')} compact />
            ))}
          </div>
        </section>
      ) : null}

      {filtered.length === 0 ? (
        <EmptyState icon={LayoutTemplate} title="No templates found" description="Try a different search or category." />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {filtered.map((template) => (
            <TemplateCard key={template.id} template={template} onUse={() => navigate('/editor')} />
          ))}
        </div>
      )}
    </div>
  );
}

function TemplateCard({ template, onUse, compact }: { template: Template; onUse: () => void; compact?: boolean }) {
  return (
    <Card className={cn('flex flex-col', compact ? 'w-72 shrink-0' : '')}>
      <div className="relative flex h-36 items-center justify-center rounded-t-xl bg-gradient-to-br from-primary/30 to-accent/30">
        {template.featured ? <Badge variant="success" className="absolute top-2 left-2">Featured</Badge> : null}
        <span className="flex h-10 w-10 items-center justify-center rounded-full bg-surface/80">
          <Play className="h-4 w-4 text-content" />
        </span>
      </div>
      <div className="flex flex-1 flex-col p-4">
        <h3 className="truncate font-medium text-content">{template.name}</h3>
        <div className="mt-2 flex items-center gap-2 text-xs text-subtle">
          <Badge variant="neutral">{template.category}</Badge>
          <span className="flex items-center gap-1">
            <Star className="h-3.5 w-3.5 fill-current text-amber-500" /> {template.rating.toFixed(1)}
          </span>
          <span>{formatNumber(template.downloads)} downloads</span>
        </div>
        <div className="mt-4 flex items-center justify-between gap-2">
          {template.price === 0 ? (
            <Badge variant="success">Free</Badge>
          ) : (
            <span className="font-semibold text-content">${template.price.toFixed(2)}</span>
          )}
          <Button size="sm" onClick={onUse}>
            <LayoutTemplate className="h-4 w-4" /> Use template
          </Button>
        </div>
      </div>
    </Card>
  );
}
