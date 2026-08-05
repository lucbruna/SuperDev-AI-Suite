import type {
  AnalyticsSummary,
  Asset,
  Collaborator,
  Project,
  RenderJob,
  Template,
  User,
  VoiceProfile,
} from '@/types';

const API_BASE = '/api/v1/video-studio';

/** Fetch JSON from the real module API; returns null on any failure. */
async function fetchJson<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      headers: { Accept: 'application/json' },
    });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

// ── Raw backend shapes (snake_case contract) ──────────────────────

interface RawProject {
  id: string;
  name: string;
  description?: string | null;
  status: string;
  resolution: string;
  aspect_ratio: string;
  frame_rate: number;
  duration_seconds: number;
  thumbnail_url?: string | null;
  output_url?: string | null;
  scene_count: number;
}

interface RawAsset {
  id: string;
  project_id: string;
  name: string;
  asset_type: string;
  mime_type?: string | null;
  file_path: string;
  file_size_bytes: number;
  thumbnail_url?: string | null;
}

interface RawRenderJob {
  id: string;
  project_id: string;
  status: string;
  progress: number; // 0..1
  output_format: string;
  output_resolution: string;
  use_gpu: boolean;
  started_at?: string | null;
  completed_at?: string | null;
}

interface RawVoice {
  id: string;
  name: string;
  gender: string;
  language: string;
  style: string[];
  description: string;
}

// ── Normalizers (backend contract → frontend domain types) ────────

const PROJECT_STATUSES: readonly Project['status'][] = [
  'draft',
  'active',
  'rendering',
  'published',
];

function normalizeProject(raw: RawProject): Project {
  const status = PROJECT_STATUSES.includes(raw.status as Project['status'])
    ? (raw.status as Project['status'])
    : 'draft';
  return {
    id: raw.id,
    title: raw.name,
    description: raw.description ?? undefined,
    status,
    updatedAt: new Date().toISOString(), // backend exposes no timestamp yet
    thumbnail: raw.thumbnail_url ?? undefined,
    ownerId: 'u1',
  };
}

const ASSET_TYPES: readonly Asset['type'][] = [
  'video',
  'image',
  'audio',
  'voice',
  'avatar',
  'template',
  'effect',
  'transition',
  'font',
  'logo',
  'subtitle',
];

function normalizeAsset(raw: RawAsset): Asset {
  const type = ASSET_TYPES.includes(raw.asset_type as Asset['type'])
    ? (raw.asset_type as Asset['type'])
    : 'video';
  return {
    id: raw.id,
    name: raw.name,
    type,
    size: raw.file_size_bytes,
    thumbnail: raw.thumbnail_url ?? undefined,
    createdAt: new Date().toISOString(), // backend exposes no timestamp yet
  };
}

const RENDER_STATUSES: Record<string, RenderJob['status']> = {
  queued: 'queued',
  rendering: 'rendering',
  completed: 'done',
  done: 'done',
  failed: 'failed',
  cancelled: 'failed',
};

function normalizeRenderJob(raw: RawRenderJob): RenderJob {
  return {
    id: raw.id,
    projectId: raw.project_id,
    title: `${raw.output_format.toUpperCase()} · ${raw.output_resolution}`,
    status: RENDER_STATUSES[raw.status] ?? 'queued',
    progress: Math.round(raw.progress * 100),
    resolution: raw.output_resolution,
    fps: 30, // backend render records do not carry fps
    startedAt: raw.started_at ?? undefined,
    finishedAt: raw.completed_at ?? undefined,
    gpu: raw.use_gpu ? 'GPU' : undefined,
  };
}

const VOICE_GENDERS: readonly VoiceProfile['gender'][] = ['male', 'female', 'neutral'];

function normalizeVoice(raw: RawVoice): VoiceProfile {
  const gender = VOICE_GENDERS.includes(raw.gender as VoiceProfile['gender'])
    ? (raw.gender as VoiceProfile['gender'])
    : 'neutral';
  return {
    id: raw.id,
    name: raw.name,
    language: raw.language,
    gender,
    emotion: raw.style.length > 0 ? raw.style.join(', ') : 'neutral',
  };
}

// ── Mocks (fallback when the backend is unreachable) ───────────────

const MOCK_PROJECTS: Project[] = [
  { id: 'p1', title: 'Product Launch 2026', status: 'active', updatedAt: new Date(Date.now() - 3_600_000).toISOString(), ownerId: 'u1', collaborators: 4 },
  { id: 'p2', title: 'Brand Story — Agriculture', status: 'published', updatedAt: new Date(Date.now() - 86_400_000).toISOString(), ownerId: 'u1', collaborators: 2 },
  { id: 'p3', title: 'Finance Explainer Series', status: 'rendering', updatedAt: new Date(Date.now() - 7_200_000).toISOString(), ownerId: 'u1', collaborators: 3 },
  { id: 'p4', title: 'Ecommerce Ads Q3', status: 'draft', updatedAt: new Date(Date.now() - 172_800_000).toISOString(), ownerId: 'u1', collaborators: 1 },
];

const MOCK_ASSETS: Asset[] = [
  { id: 'a1', name: 'hero_broll.mp4', type: 'video', size: 4_200_000_000, createdAt: new Date().toISOString(), tags: ['broll'] },
  { id: 'a2', name: 'logo_white.svg', type: 'logo', size: 18_000, createdAt: new Date().toISOString() },
  { id: 'a3', name: 'voiceover_final.wav', type: 'voice', size: 24_000_000, createdAt: new Date().toISOString() },
  { id: 'a4', name: 'avatar_maria', type: 'avatar', size: 3_200_000, createdAt: new Date().toISOString() },
];

const MOCK_RENDER_JOBS: RenderJob[] = [
  { id: 'r1', projectId: 'p1', title: 'Product Launch 2026 — 4K', status: 'rendering', progress: 64, resolution: '3840x2160', fps: 30, gpu: 'RTX 4090' },
  { id: 'r2', projectId: 'p2', title: 'Brand Story — 1080p', status: 'done', progress: 100, resolution: '1920x1080', fps: 60, gpu: 'RTX 4090' },
  { id: 'r3', projectId: 'p3', title: 'Finance Series — 1080p', status: 'queued', progress: 0, resolution: '1920x1080', fps: 30 },
];

const MOCK_TEMPLATES: Template[] = [
  { id: 't1', name: 'Modern Business Intro', category: 'Business', downloads: 1240, rating: 4.8, price: 0, featured: true },
  { id: 't2', name: 'Farming Stories', category: 'Agriculture', downloads: 860, rating: 4.6, price: 12.9 },
  { id: 't3', name: 'Clinic Explainer', category: 'Healthcare', downloads: 540, rating: 4.5, price: 15.0 },
  { id: 't4', name: 'Shop Drops', category: 'Ecommerce', downloads: 2310, rating: 4.9, price: 0, featured: true },
];

const MOCK_USERS: User[] = [
  { id: 'u1', name: 'Ana Souza', email: 'ana@superdev.app', role: 'owner', status: 'active', lastActive: new Date().toISOString() },
  { id: 'u2', name: 'Bruno Lima', email: 'bruno@superdev.app', role: 'editor', status: 'active', lastActive: new Date(Date.now() - 3_600_000).toISOString() },
  { id: 'u3', name: 'Carla Mendes', email: 'carla@superdev.app', role: 'viewer', status: 'invited' },
];

const MOCK_VOICES: VoiceProfile[] = [
  { id: 'v1', name: 'Mariana — PT-BR', language: 'pt-BR', gender: 'female', emotion: 'neutral' },
  { id: 'v2', name: 'Daniel — EN-US', language: 'en-US', gender: 'male', emotion: 'energetic' },
  { id: 'v3', name: 'Lucas — PT-BR', language: 'pt-BR', gender: 'male', emotion: 'calm' },
];

const MOCK_ANALYTICS: AnalyticsSummary = {
  views: 1_240_000,
  watchTime: 3_620_000,
  likes: 84_200,
  comments: 12_400,
  shares: 31_800,
  subscribers: 156_000,
};

const MOCK_COLLABORATORS: Collaborator[] = [
  { id: 'c1', user: MOCK_USERS[1], permission: 'project:write', joinedAt: new Date().toISOString() },
  { id: 'c2', user: MOCK_USERS[2], permission: 'project:read', joinedAt: new Date().toISOString() },
];

// ── Public fetchers ────────────────────────────────────────────────

export async function fetchProjects(): Promise<Project[]> {
  const raw = await fetchJson<RawProject[]>('/projects/');
  return raw ? raw.map(normalizeProject) : MOCK_PROJECTS;
}

export async function fetchAssets(): Promise<Asset[]> {
  const raw = await fetchJson<RawAsset[]>('/assets/');
  return raw ? raw.map(normalizeAsset) : MOCK_ASSETS;
}

export async function fetchRenderJobs(): Promise<RenderJob[]> {
  const raw = await fetchJson<RawRenderJob[]>('/render/');
  return raw ? raw.map(normalizeRenderJob) : MOCK_RENDER_JOBS;
}

export async function fetchTemplates(): Promise<Template[]> {
  const raw = await fetchJson<Template[]>('/marketplace/templates');
  return raw ?? MOCK_TEMPLATES;
}

export async function fetchUsers(): Promise<User[]> {
  const raw = await fetchJson<User[]>('/admin/users');
  return raw ?? MOCK_USERS;
}

export async function fetchVoiceProfiles(): Promise<VoiceProfile[]> {
  const body = await fetchJson<{ data?: { voices?: RawVoice[] } }>('/audio/voices');
  const voices = body?.data?.voices;
  return voices && voices.length > 0 ? voices.map(normalizeVoice) : MOCK_VOICES;
}

export async function fetchAnalytics(): Promise<AnalyticsSummary> {
  const raw = await fetchJson<AnalyticsSummary>('/analytics/summary');
  return raw ?? MOCK_ANALYTICS;
}

export async function fetchCollaborators(): Promise<Collaborator[]> {
  const raw = await fetchJson<Collaborator[]>('/collaboration/members');
  return raw ?? MOCK_COLLABORATORS;
}
