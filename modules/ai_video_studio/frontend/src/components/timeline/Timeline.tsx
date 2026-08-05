import { useState } from 'react';
import { Clapperboard, Clock } from 'lucide-react';
import { formatDuration } from '@/utils';
import { useInterval } from '@/hooks';
import ClipBlock from './ClipBlock';
import Playhead from './Playhead';
import TrackList from './TrackList';
import ZoomControls from './ZoomControls';

export interface TimelineClip {
  id: string;
  name: string;
  start: number;
  duration: number;
  color: string;
}

export interface TimelineTrack {
  id: string;
  name: string;
  type: 'video' | 'audio' | 'text';
  clips: TimelineClip[];
}

const TOTAL_SECONDS = 32;
const BASE_PX_PER_SECOND = 14;
const MARK_STEP = 2;

const TRACKS: TimelineTrack[] = [
  {
    id: 'video-main',
    name: 'Video',
    type: 'video',
    clips: [
      { id: 'c1', name: 'Intro', start: 0, duration: 6, color: 'bg-primary/60' },
      { id: 'c2', name: 'Features', start: 6, duration: 10, color: 'bg-accent/60' },
      { id: 'c3', name: 'CTA', start: 16, duration: 6, color: 'bg-primary/60' },
    ],
  },
  {
    id: 'video-overlay',
    name: 'Overlay',
    type: 'video',
    clips: [{ id: 'c4', name: 'Logo', start: 2, duration: 8, color: 'bg-sky-500/50' }],
  },
  {
    id: 'voice',
    name: 'Voiceover',
    type: 'audio',
    clips: [{ id: 'c5', name: 'Narration', start: 0, duration: 22, color: 'bg-emerald-500/50' }],
  },
  {
    id: 'music',
    name: 'Music',
    type: 'audio',
    clips: [{ id: 'c6', name: 'Bed track', start: 0, duration: 32, color: 'bg-violet-500/50' }],
  },
  {
    id: 'text',
    name: 'Captions',
    type: 'text',
    clips: [{ id: 'c7', name: 'Subtitles', start: 4, duration: 18, color: 'bg-amber-500/50' }],
  },
];

const round2 = (value: number) => Math.round(value * 100) / 100;

export default function Timeline() {
  const [zoom, setZoom] = useState(1);
  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const pxPerSecond = BASE_PX_PER_SECOND * zoom;
  const totalPx = TOTAL_SECONDS * pxPerSecond;
  const markCount = Math.floor(TOTAL_SECONDS / MARK_STEP) + 1;

  useInterval(() => {
    if (!isPlaying) return;
    setCurrentTime((time) => (time + 0.1 >= TOTAL_SECONDS ? 0 : round2(time + 0.1)));
  }, 100);

  const handleSeek = (clientX: number, element: HTMLDivElement) => {
    const rect = element.getBoundingClientRect();
    const px = clientX - rect.left;
    setCurrentTime(Math.max(0, Math.min(TOTAL_SECONDS, px / pxPerSecond)));
  };

  return (
    <div className="flex h-full flex-col bg-panel">
      <div className="flex h-10 shrink-0 items-center justify-between border-b border-border px-3">
        <div className="flex items-center gap-2">
          <Clapperboard className="h-4 w-4 text-primary" />
          <span className="text-xs font-semibold uppercase tracking-wide text-subtle">Timeline</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-xs tabular-nums text-subtle">
            <Clock className="h-3.5 w-3.5" />
            {formatDuration(currentTime)} / {formatDuration(TOTAL_SECONDS)}
          </span>
          <ZoomControls zoom={zoom} onChange={setZoom} />
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-hidden">
        <div className="flex h-full">
          <TrackList tracks={TRACKS} />
          <div className="min-w-0 flex-1 overflow-auto">
            <div className="relative" style={{ width: totalPx, minWidth: '100%' }}>
              <Playhead currentTime={currentTime} pxPerSecond={pxPerSecond} />
              <div
                className="sticky top-0 z-10 flex h-6 cursor-col-resize border-b border-border bg-surface"
                onPointerDown={(event) => handleSeek(event.clientX, event.currentTarget)}
              >
                {Array.from({ length: markCount }, (_, index) => {
                  const seconds = index * MARK_STEP;
                  return (
                    <div key={seconds} className="absolute top-0 h-full border-l border-border/40" style={{ left: seconds * pxPerSecond }}>
                      <span className="absolute left-1 top-0.5 text-[9px] tabular-nums text-subtle">{formatDuration(seconds)}</span>
                    </div>
                  );
                })}
              </div>
              {TRACKS.map((track) => (
                <div
                  key={track.id}
                  className="relative h-12 border-b border-border/50"
                  onPointerDown={(event) => handleSeek(event.clientX, event.currentTarget)}
                >
                  {track.clips.map((clip) => (
                    <ClipBlock key={clip.id} clip={clip} pxPerSecond={pxPerSecond} />
                  ))}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
