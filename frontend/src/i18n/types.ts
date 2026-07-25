export type Locale = "pt-BR" | "en" | "es";

export interface TranslationKeys {
  // Geral
  common: {
    save: string;
    cancel: string;
    delete: string;
    edit: string;
    create: string;
    search: string;
    loading: string;
    error: string;
    success: string;
    confirm: string;
    yes: string;
    no: string;
    back: string;
    next: string;
    finish: string;
  };
  // Autenticação
  auth: {
    login: string;
    logout: string;
    register: string;
    email: string;
    password: string;
    forgotPassword: string;
    resetPassword: string;
    loginSuccess: string;
    loginError: string;
    registerSuccess: string;
  };
  // Navegação
  nav: {
    home: string;
    dashboard: string;
    projects: string;
    agents: string;
    workflows: string;
    plugins: string;
    settings: string;
    admin: string;
    help: string;
  };
  // Projetos
  projects: {
    title: string;
    create: string;
    list: string;
    name: string;
    description: string;
    status: string;
    empty: string;
  };
  // Agentes
  agents: {
    title: string;
    list: string;
    start: string;
    stop: string;
    logs: string;
    status: string;
    idle: string;
    running: string;
    error: string;
  };
  // Workflows
  workflows: {
    title: string;
    create: string;
    run: string;
    stop: string;
    history: string;
    status: string;
  };
  // Configurações
  settings: {
    title: string;
    general: string;
    appearance: string;
    language: string;
    security: string;
    providers: string;
    notifications: string;
  };
  // Erros
  errors: {
    notFound: string;
    unauthorized: string;
    forbidden: string;
    serverError: string;
    networkError: string;
    validationError: string;
  };
}
