import { create } from 'zustand';
import type { Notification, Project, ThemeName, User } from '@/types';

const now = new Date().toISOString();

const CURRENT_USER: User = {
  id: 'u1',
  name: 'Ana Souza',
  email: 'ana@superdev.app',
  role: 'owner',
  status: 'active',
  lastActive: now,
};

interface AppState {
  user: User | null;
  theme: ThemeName;
  notifications: Notification[];
  projects: Project[];
  setUser: (user: User | null) => void;
  setTheme: (theme: ThemeName) => void;
  addNotification: (notification: Omit<Notification, 'id' | 'read' | 'createdAt'>) => void;
  markNotificationRead: (id: string) => void;
  markAllNotificationsRead: () => void;
  setProjects: (projects: Project[]) => void;
  updateProject: (id: string, patch: Partial<Project>) => void;
}

export const useAppStore = create<AppState>((set) => ({
  user: CURRENT_USER,
  theme: 'dark-enterprise',
  notifications: [
    {
      id: 'n1',
      kind: 'success',
      title: 'Render completed',
      body: 'Product Launch 2026 — 4K is ready to download.',
      read: false,
      createdAt: now,
    },
    {
      id: 'n2',
      kind: 'info',
      title: 'New template available',
      body: 'Shop Drops is now featured in the marketplace.',
      read: false,
      createdAt: now,
    },
    {
      id: 'n3',
      kind: 'warning',
      title: 'Storage at 82%',
      body: 'Consider cleaning up unused assets.',
      read: true,
      createdAt: now,
    },
  ],
  projects: [],
  setUser: (user) => set({ user }),
  setTheme: (theme) => set({ theme }),
  addNotification: (notification) =>
    set((state) => ({
      notifications: [
        { ...notification, id: `n_${Math.random().toString(36).slice(2, 9)}`, read: false, createdAt: now },
        ...state.notifications,
      ],
    })),
  markNotificationRead: (id) =>
    set((state) => ({
      notifications: state.notifications.map((n) => (n.id === id ? { ...n, read: true } : n)),
    })),
  markAllNotificationsRead: () =>
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, read: true })),
    })),
  setProjects: (projects) => set({ projects }),
  updateProject: (id, patch) =>
    set((state) => ({
      projects: state.projects.map((p) => (p.id === id ? { ...p, ...patch } : p)),
    })),
}));
