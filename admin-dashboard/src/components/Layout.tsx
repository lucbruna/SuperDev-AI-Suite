import { useEffect, useMemo, useState, type ReactNode } from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Building2,
  FolderKanban,
  Workflow,
  Bot,
  BookOpen,
  Puzzle,
  Flag,
  Settings,
  Search,
  Sun,
  Moon,
  LogOut,
  ChevronsLeft,
  ChevronsRight,
  Menu,
  X,
  Sparkles,
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useTheme } from './ThemeProvider';
import { CommandPalette } from './CommandPalette';
import { NotificationCenter } from './NotificationCenter';
import { cn } from '../lib/utils';
import type { LucideIcon } from 'lucide-react';

interface NavItem {
  label: string;
  path: string;
  icon: LucideIcon;
  section: string;
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Visão Geral', path: '/dashboard', icon: LayoutDashboard, section: 'Principal' },
  { label: 'Organizações', path: '/organizations', icon: Building2, section: 'Gerenciamento' },
  { label: 'Projetos', path: '/projects', icon: FolderKanban, section: 'Gerenciamento' },
  { label: 'Workflows', path: '/workflows', icon: Workflow, section: 'Automação' },
  { label: 'Agentes', path: '/agents', icon: Bot, section: 'Automação' },
  { label: 'Base de Conhecimento', path: '/knowledge-base', icon: BookOpen, section: 'Gerenciamento' },
  { label: 'Plugins', path: '/plugins', icon: Puzzle, section: 'Gerenciamento' },
  { label: 'Feature Flags', path: '/feature-flags', icon: Flag, section: 'Configuração' },
  { label: 'Configurações', path: '/settings', icon: Settings, section: 'Configuração' },
];

const SECTION_ORDER = ['Principal', 'Gerenciamento', 'Automação', 'Configuração'];

/** Shell principal do admin dashboard: sidebar colapsável + header (busca global, notificações, tema, usuário). */
export function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  // Atalho global Ctrl/Cmd+K para abrir a busca
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setPaletteOpen((o) => !o);
      }
      if (e.key === 'Escape') {
        setPaletteOpen(false);
        setUserMenuOpen(false);
      }
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, []);

  // Fecha menu mobile ao navegar
  useEffect(() => {
    setMobileOpen(false);
    setUserMenuOpen(false);
  }, [location.pathname]);

  const grouped = useMemo(() => {
    const map = new Map<string, NavItem[]>();
    for (const item of NAV_ITEMS) {
      const list = map.get(item.section) ?? [];
      list.push(item);
      map.set(item.section, list);
    }
    return SECTION_ORDER.filter((s) => map.has(s)).map((s) => ({ section: s, items: map.get(s)! }));
  }, []);

  const current = NAV_ITEMS.find((i) => location.pathname.startsWith(i.path));

  const initials = useMemo(() => {
    const name = user?.fullName || user?.username || user?.email || 'U';
    return name
      .split(/[\s@.]+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((p) => p[0]!.toUpperCase())
      .join('');
  }, [user]);

  const sidebarContent = (
    <div className="flex h-full flex-col">
      <div className={cn('flex items-center gap-3 border-b border-slate-700/50 px-4 py-4', collapsed && 'justify-center px-2')}>
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 shadow-md shadow-indigo-500/30">
          <Sparkles className="h-5 w-5 text-white" />
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <p className="truncate text-sm font-bold text-white">SuperDev</p>
            <p className="truncate text-[11px] text-slate-400">Administração</p>
          </div>
        )}
      </div>

      <nav className="flex-1 space-y-4 overflow-y-auto scrollbar-thin px-3 py-4">
        {grouped.map(({ section, items }) => (
          <div key={section}>
            {!collapsed && (
              <p className="mb-1.5 px-2 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                {section}
              </p>
            )}
            <ul className="space-y-0.5">
              {items.map((item) => (
                <li key={item.path}>
                  <NavLink
                    to={item.path}
                    title={collapsed ? item.label : undefined}
                    className={({ isActive }) =>
                      cn(
                        'group flex items-center gap-3 rounded-lg px-2.5 py-2 text-sm transition',
                        collapsed && 'justify-center px-0',
                        isActive
                          ? 'bg-indigo-500/15 font-medium text-indigo-300'
                          : 'text-slate-300 hover:bg-slate-700/40 hover:text-white'
                      )
                    }
                  >
                    <item.icon className="h-[18px] w-[18px] shrink-0" />
                    {!collapsed && <span className="truncate">{item.label}</span>}
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>

      <div className="border-t border-slate-700/50 p-3">
        <button
          onClick={() => setCollapsed((c) => !c)}
          className="hidden w-full items-center justify-center gap-2 rounded-lg px-2.5 py-2 text-sm text-slate-400 transition hover:bg-slate-700/40 hover:text-white md:flex"
        >
          {collapsed ? <ChevronsRight className="h-4 w-4" /> : <ChevronsLeft className="h-4 w-4" />}
          {!collapsed && <span>Recolher</span>}
        </button>
      </div>
    </div>
  );

  return (
    <div className="flex min-h-screen bg-surface-alt">
      {/* Sidebar desktop */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-30 hidden bg-slate-900 transition-all duration-200 md:block',
          collapsed ? 'w-16' : 'w-60'
        )}
      >
        {sidebarContent}
      </aside>

      {/* Sidebar mobile */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm animate-fade-in" onClick={() => setMobileOpen(false)} />
          <aside className="absolute inset-y-0 left-0 w-64 animate-slide-in-left">
            {sidebarContent}
            <button
              onClick={() => setMobileOpen(false)}
              className="absolute right-3 top-4 rounded-lg p-1.5 text-slate-400 hover:text-white"
              aria-label="Fechar menu"
            >
              <X className="h-5 w-5" />
            </button>
          </aside>
        </div>
      )}

      <div className={cn('flex min-w-0 flex-1 flex-col transition-all duration-200', collapsed ? 'md:pl-16' : 'md:pl-60')}>
        {/* Header */}
        <header className="sticky top-0 z-20 border-b border-line bg-surface/80 backdrop-blur-md">
          <div className="flex h-16 items-center gap-3 px-4 lg:px-6">
            <button
              onClick={() => setMobileOpen(true)}
              className="rounded-lg border border-line p-2 text-ink-muted transition hover:text-ink md:hidden"
              aria-label="Abrir menu"
            >
              <Menu className="h-5 w-5" />
            </button>

            {/* Breadcrumb */}
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-ink">{current?.label ?? 'SuperDev'}</p>
              <p className="hidden text-xs text-ink-muted sm:block">
                {current ? current.section : 'Administração'}
              </p>
            </div>

            {/* Busca global */}
            <button
              onClick={() => setPaletteOpen(true)}
              className="ml-auto flex h-9 w-40 items-center gap-2 rounded-lg border border-line bg-surface-alt px-3 text-sm text-ink-muted transition hover:border-primary-300 hover:text-ink sm:w-64"
            >
              <Search className="h-4 w-4 shrink-0" />
              <span className="hidden truncate sm:block">Buscar...</span>
              <kbd className="ml-auto hidden rounded border border-line bg-surface px-1.5 py-0.5 text-[10px] text-ink-muted sm:block">
                Ctrl K
              </kbd>
            </button>

            <NotificationCenter />

            <button
              onClick={toggleTheme}
              className="flex h-9 w-9 items-center justify-center rounded-lg border border-line bg-surface-alt text-ink-muted transition hover:text-ink"
              aria-label="Alternar tema"
            >
              {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>

            {/* Menu do usuário */}
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen((o) => !o)}
                className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 text-xs font-bold text-white ring-2 ring-primary-200 transition hover:ring-primary-300 dark:ring-primary-800"
                aria-label="Menu do usuário"
              >
                {initials}
              </button>
              {userMenuOpen && (
                <div className="absolute right-0 top-12 z-40 w-56 overflow-hidden rounded-xl border border-line bg-surface shadow-popover animate-slide-up">
                  <div className="border-b border-line px-4 py-3">
                    <p className="truncate text-sm font-semibold text-ink">
                      {user?.fullName || user?.username || 'Usuário'}
                    </p>
                    <p className="truncate text-xs text-ink-muted">{user?.email ?? '—'}</p>
                  </div>
                  <div className="p-1.5">
                    <button
                      onClick={() => {
                        setUserMenuOpen(false);
                        navigate('/settings');
                      }}
                      className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-ink transition hover:bg-surface-alt"
                    >
                      <Settings className="h-4 w-4 text-ink-muted" /> Configurações
                    </button>
                    <button
                      onClick={() => void logout()}
                      className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-danger-600 transition hover:bg-danger-50 dark:text-danger-400 dark:hover:bg-danger-500/10"
                    >
                      <LogOut className="h-4 w-4" /> Sair
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        <main className="flex-1 px-4 py-6 lg:px-6">{children}</main>

        <footer className="border-t border-line px-6 py-4 text-center text-xs text-ink-muted">
          SuperDev Admin · Painel administrativo
        </footer>
      </div>

      <CommandPalette open={paletteOpen} onClose={() => setPaletteOpen(false)} />
    </div>
  );
}

export default Layout;
