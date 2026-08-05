import type { Translation } from './types';

export const translations: Translation = {
  appName: 'SuperDev AI Video Studio',
  tagline: 'Create, edit and publish AI-powered video at scale',
  nav: {
    dashboard: 'Dashboard',
    projects: 'Projects',
    editor: 'Editor',
    assets: 'Assets',
    marketplace: 'Marketplace',
    avatarStudio: 'Avatar Studio',
    voiceStudio: 'Voice Studio',
    renderCenter: 'Render Center',
    analytics: 'Analytics',
    collaboration: 'Collaboration',
    settings: 'Settings',
    admin: 'Admin',
  },
  common: {
    save: 'Save',
    cancel: 'Cancel',
    delete: 'Delete',
    edit: 'Edit',
    create: 'Create',
    search: 'Search',
    add: 'Add',
    share: 'Share',
    export: 'Export',
    loading: 'Loading…',
    actions: 'Actions',
  },
  status: {
    draft: 'Draft',
    active: 'Active',
    rendering: 'Rendering',
    published: 'Published',
    queued: 'Queued',
    done: 'Done',
    failed: 'Failed',
  },
  auth: {
    login: 'Sign in',
    email: 'Email',
    password: 'Password',
    signIn: 'Sign in',
    welcomeBack: 'Welcome back',
  },
  editor: {
    timeline: 'Timeline',
    preview: 'Preview',
    aiAssistant: 'AI Assistant',
    generateScript: 'Generate script',
    generateVoice: 'Generate voiceover',
    suggestedAssets: 'Suggested assets',
  },
  dashboard: {
    title: 'Dashboard',
    recentProjects: 'Recent projects',
  },
};

export default translations;
