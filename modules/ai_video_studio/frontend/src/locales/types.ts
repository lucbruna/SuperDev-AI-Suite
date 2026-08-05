export interface Translation {
  appName: string;
  tagline: string;
  nav: {
    dashboard: string;
    projects: string;
    editor: string;
    assets: string;
    marketplace: string;
    avatarStudio: string;
    voiceStudio: string;
    renderCenter: string;
    analytics: string;
    collaboration: string;
    settings: string;
    admin: string;
  };
  common: {
    save: string;
    cancel: string;
    delete: string;
    edit: string;
    create: string;
    search: string;
    add: string;
    share: string;
    export: string;
    loading: string;
    actions: string;
  };
  status: {
    draft: string;
    active: string;
    rendering: string;
    published: string;
    queued: string;
    done: string;
    failed: string;
  };
  auth: {
    login: string;
    email: string;
    password: string;
    signIn: string;
    welcomeBack: string;
  };
  editor: {
    timeline: string;
    preview: string;
    aiAssistant: string;
    generateScript: string;
    generateVoice: string;
    suggestedAssets: string;
  };
  dashboard: {
    title: string;
    recentProjects: string;
  };
}
