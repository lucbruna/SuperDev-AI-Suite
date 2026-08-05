import { useEffect, useState } from 'react';
import { Eye, Heart, MessageCircle, Play, Share2, ThumbsUp, Users } from 'lucide-react';
import type { AnalyticsSummary } from '@/types';
import { fetchAnalytics } from '@/api';
import { formatDuration, formatNumber } from '@/utils';
import { Card, CardBody, CardHeader, ProgressBar, SectionHeader, StatCard, Tabs } from '@/ui';

const TREND = [42, 58, 51, 66, 72, 64, 80, 76, 88, 82, 95, 100];

const TOP_VIDEOS = [
  { id: 'v1', title: 'Product Launch 2026 — Teaser', views: 412_000, watch: 68, likes: 28_400, comments: 3_900 },
  { id: 'v2', title: 'Farming Stories — Episode 4', views: 288_000, watch: 61, likes: 19_200, comments: 2_100 },
  { id: 'v3', title: 'Finance Explainer — Budgeting', views: 175_000, watch: 55, likes: 12_600, comments: 1_450 },
  { id: 'v4', title: 'Shop Drops — Summer Edit', views: 121_000, watch: 72, likes: 9_800, comments: 980 },
];

export default function Analytics() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [range, setRange] = useState('30d');

  useEffect(() => {
    fetchAnalytics().then(setSummary);
  }, []);

  return (
    <div>
      <SectionHeader
        title="Analytics"
        subtitle="Channel and video performance"
        action={<Tabs tabs={[{ id: '7d', label: '7 days' }, { id: '30d', label: '30 days' }, { id: '90d', label: '90 days' }]} value={range} onChange={setRange} />}
      />

      <div className="mb-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <StatCard label="Views" value={formatNumber(summary?.views ?? 0)} icon={Eye} trend="up" delta="12.4%" />
        <StatCard label="Watch time" value={formatDuration(summary?.watchTime ?? 0)} icon={Play} trend="up" delta="8.1%" />
        <StatCard label="Likes" value={formatNumber(summary?.likes ?? 0)} icon={ThumbsUp} trend="up" delta="5.3%" />
        <StatCard label="Shares" value={formatNumber(summary?.shares ?? 0)} icon={Share2} trend="down" delta="1.2%" />
        <StatCard label="Subscribers" value={formatNumber(summary?.subscribers ?? 0)} icon={Users} trend="up" delta="3.2%" />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader title="Views trend" subtitle={`Last ${range.replace('d', ' days')}`} />
          <CardBody>
            <div className="flex h-64 items-end gap-2">
              {TREND.map((value, index) => (
                <div key={index} className="flex flex-1 flex-col items-center gap-2">
                  <div className="flex w-full flex-1 items-end">
                    <div className="w-full rounded-t bg-primary/70 transition-colors hover:bg-accent" style={{ height: `${value}%` }} />
                  </div>
                  {index % 3 === 0 ? <span className="text-[10px] text-subtle">W{index + 1}</span> : null}
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Audience" />
          <CardBody className="space-y-5">
            <div className="space-y-2">
              <div className="flex justify-between text-sm"><span className="text-content">New viewers</span><span className="text-subtle">54%</span></div>
              <ProgressBar value={54} variant="accent" />
              <div className="flex justify-between text-sm"><span className="text-content">Returning</span><span className="text-subtle">31%</span></div>
              <ProgressBar value={31} />
              <div className="flex justify-between text-sm"><span className="text-content">Subscribers</span><span className="text-subtle">15%</span></div>
              <ProgressBar value={15} />
            </div>
            <div className="space-y-2 border-t border-border pt-4">
              {[
                { label: '18–24', value: 22 },
                { label: '25–34', value: 38 },
                { label: '35–44', value: 26 },
                { label: '45+', value: 14 },
              ].map((row) => (
                <div key={row.label} className="flex items-center gap-3 text-sm">
                  <span className="w-12 text-subtle">{row.label}</span>
                  <ProgressBar value={row.value} />
                  <span className="w-10 text-right text-subtle">{row.value}%</span>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader title="Top videos" />
        <CardBody className="divide-y divide-border">
          {TOP_VIDEOS.map((video) => (
            <div key={video.id} className="flex flex-wrap items-center gap-4 py-3">
              <span className="flex h-10 w-16 shrink-0 items-center justify-center rounded-md bg-gradient-to-br from-primary/30 to-accent/30">
                <Play className="h-3.5 w-3.5 text-content" />
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-content">{video.title}</p>
                <div className="mt-1 flex items-center gap-3 text-xs text-subtle">
                  <span>{formatNumber(video.views)} views</span>
                  <span className="flex items-center gap-1"><Heart className="h-3 w-3" />{formatNumber(video.likes)}</span>
                  <span className="flex items-center gap-1"><MessageCircle className="h-3 w-3" />{formatNumber(video.comments)}</span>
                </div>
              </div>
              <div className="w-40">
                <p className="mb-1 text-xs text-subtle">Watch %</p>
                <ProgressBar value={video.watch} />
              </div>
            </div>
          ))}
        </CardBody>
      </Card>
    </div>
  );
}
