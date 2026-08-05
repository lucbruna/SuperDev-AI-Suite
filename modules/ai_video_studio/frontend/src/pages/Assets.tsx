import { useEffect, useMemo, useState } from 'react';
import {
  AudioLines,
  Download,
  Figma,
  FileText,
  Image,
  LayoutTemplate,
  Mic,
  MoreHorizontal,
  MoveRight,
  Trash2,
  Type,
  Upload,
  UploadCloud,
  UserRound,
  Video,
  Wand2,
} from 'lucide-react';
import type { Asset, AssetType } from '@/types';
import { ASSET_TYPES } from '@/constants';
import { fetchAssets } from '@/api';
import { useDebounce } from '@/hooks';
import { cn, formatBytes, formatDate } from '@/utils';
import { Badge, Button, Card, EmptyState, IconButton, Input, SectionHeader, Tabs } from '@/ui';

const typeIcons: Record<AssetType, typeof Video> = {
  video: Video,
  image: Image,
  audio: AudioLines,
  voice: Mic,
  avatar: UserRound,
  template: LayoutTemplate,
  effect: Wand2,
  transition: MoveRight,
  font: Type,
  logo: Figma,
  subtitle: FileText,
};

export default function Assets() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [query, setQuery] = useState('');
  const [type, setType] = useState('all');
  const debouncedQuery = useDebounce(query, 250);

  useEffect(() => {
    fetchAssets().then(setAssets);
  }, []);

  const filtered = useMemo(
    () =>
      assets.filter((asset) => {
        const matchesType = type === 'all' || asset.type === type;
        const matchesQuery = asset.name.toLowerCase().includes(debouncedQuery.toLowerCase());
        return matchesType && matchesQuery;
      }),
    [assets, type, debouncedQuery],
  );

  return (
    <div>
      <SectionHeader
        title="Assets"
        subtitle="Library of media for your projects"
        action={
          <Button>
            <Upload className="h-4 w-4" /> Upload
          </Button>
        }
      />

      <div className="mb-6 flex items-center justify-center rounded-xl border-2 border-dashed border-border bg-panel/50 p-6 text-center">
        <div className="text-subtle">
          <UploadCloud className="mx-auto mb-2 h-8 w-8" />
          <p className="text-sm">Drag &amp; drop files here or click to browse</p>
        </div>
      </div>

      <div className="mb-6 flex flex-wrap items-center gap-3">
        <Input className="w-72" placeholder="Search assets..." value={query} onChange={(event) => setQuery(event.target.value)} />
        <Tabs
          tabs={[{ id: 'all', label: 'All' }, ...ASSET_TYPES.map((t) => ({ id: t, label: t.charAt(0).toUpperCase() + t.slice(1) }))]}
          value={type}
          onChange={setType}
        />
      </div>

      {filtered.length === 0 ? (
        <EmptyState icon={UploadCloud} title="No assets found" description="Try a different search or upload new media." />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {filtered.map((asset) => {
            const Icon = typeIcons[asset.type];
            return (
              <Card key={asset.id} className="group relative">
                <div className="flex items-start gap-3 p-4">
                  <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-surface">
                    <Icon className="h-6 w-6 text-primary" />
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium text-content">{asset.name}</p>
                    <p className="mt-0.5 text-xs text-subtle">{formatBytes(asset.size)} · {formatDate(asset.createdAt)}</p>
                    {asset.tags && asset.tags.length > 0 ? (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {asset.tags.map((tag) => (
                          <Badge key={tag} variant="neutral">{tag}</Badge>
                        ))}
                      </div>
                    ) : null}
                  </div>
                  <Badge variant="neutral">{asset.type}</Badge>
                </div>
                <div className={cn('absolute top-2 right-2 hidden gap-1 rounded-lg bg-panel p-1 shadow', 'group-hover:flex')}>
                  <IconButton icon={Download} label="Download" size="sm" />
                  <IconButton icon={Trash2} label="Delete" size="sm" />
                  <IconButton icon={MoreHorizontal} label="More" size="sm" />
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
