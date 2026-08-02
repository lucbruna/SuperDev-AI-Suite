import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Command, CornerDownLeft, ArrowRight, FileText, Loader2 } from 'lucide-react';
import { searchApi } from '../services/api';
import { cn } from '../lib/utils';
import type { SearchResult } from '../types/api';

interface NavEntry {
  label: string;
  path: string;
  keywords: string;
  section: string;
}

const NAV_ENTRIES: NavEntry[] = [
  { label: 'Visão Geral', path: '/dashboard', keywords: 'dashboard home inicio visao geral', section: 'Navegação' },
  { label: 'Organizações', path: '/organizations', keywords: 'organizacoes orgs empresas', section: 'Navegação' },
  { label: 'Projetos', path: '/projects', keywords: 'projetos projects repos', section: 'Navegação' },
  { label: 'Workflows', path: '/workflows', keywords: 'workflows fluxos pipelines automacao', section: 'Navegação' },
  { label: 'Agentes', path: '/agents', keywords: 'agentes agents ia bots', section: 'Navegação' },
  { label: 'Base de Conhecimento', path: '/knowledge-base', keywords: 'knowledge base conhecimento rag', section: 'Navegação' },
  { label: 'Plugins', path: '/plugins', keywords: 'plugins extensoes marketplace', section: 'Navegação' },
  { label: 'Feature Flags', path: '/feature-flags', keywords: 'feature flags flags toggles', section: 'Navegação' },
  { label: 'Configurações', path: '/settings', keywords: 'configuracoes settings preferencias', section: 'Navegação' },
];

interface Props {
  open: boolean;
  onClose: () => void;
}

/** Paleta de comandos global (Ctrl+K / Cmd+K): navegação + busca real. */
export function CommandPalette({ open, onClose }: Props) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (open) {
      setQuery('');
      setResults([]);
      setActiveIndex(0);
      setTimeout(() => inputRef.current?.focus(), 10);
    }
  }, [open]);

  // Busca real com debounce (200ms)
  useEffect(() => {
    if (!open || query.trim().length < 2) {
      setResults([]);
      setSearching(false);
      return;
    }
    setSearching(true);
    const timer = setTimeout(() => {
      searchApi
        .search(query.trim(), undefined, 6)
        .then((res) => setResults(res.results ?? []))
        .catch(() => setResults([]))
        .finally(() => setSearching(false));
    }, 200);
    return () => clearTimeout(timer);
  }, [query, open]);

  const filteredNav = useMemo(() => {
    if (!query.trim()) return NAV_ENTRIES;
    const q = query.trim().toLowerCase();
    return NAV_ENTRIES.filter(
      (e) => e.label.toLowerCase().includes(q) || e.keywords.includes(q)
    );
  }, [query]);

  const totalItems = filteredNav.length + results.length;

  const go = (path: string) => {
    onClose();
    navigate(path);
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveIndex((i) => Math.min(i + 1, totalItems - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveIndex((i) => Math.max(i - 1, 0));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (activeIndex < filteredNav.length) {
        go(filteredNav[activeIndex].path);
      } else {
        const item = results[activeIndex - filteredNav.length];
        if (item?.type === 'project') go(`/projects`);
        else if (item?.type === 'agent') go(`/agents`);
        else if (item?.type === 'workflow') go(`/workflows`);
        else if (item?.type === 'knowledge') go(`/knowledge-base`);
        else if (item?.type === 'organization') go(`/organizations`);
        else if (item?.type === 'plugin') go(`/plugins`);
        else go(`/dashboard`);
      }
    }
  };

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-slate-900/50 px-4 pt-[12vh] backdrop-blur-sm animate-fade-in"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Busca global"
    >
      <div
        className="w-full max-w-xl overflow-hidden rounded-xl border border-line bg-surface shadow-popover animate-slide-up"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-3 border-b border-line px-4 py-3">
          {searching ? (
            <Loader2 className="h-4 w-4 shrink-0 animate-spin text-primary-500" />
          ) : (
            <Search className="h-4 w-4 shrink-0 text-ink-muted" />
          )}
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Buscar páginas, projetos, agentes, workflows..."
            className="w-full bg-transparent text-sm text-ink placeholder:text-ink-muted focus:outline-none"
          />
          <kbd className="hidden items-center gap-1 rounded border border-line px-1.5 py-0.5 text-[10px] text-ink-muted sm:flex">
            <Command className="h-3 w-3" /> K
          </kbd>
        </div>

        <div className="max-h-[50vh] overflow-y-auto scrollbar-thin p-2">
          {/* Navegação */}
          <p className="px-3 pb-1 pt-2 text-[11px] font-semibold uppercase tracking-wider text-ink-muted">
            {filteredNav.length > 0 ? 'Navegação' : 'Sem páginas correspondentes'}
          </p>
          {filteredNav.map((entry, i) => (
            <button
              key={entry.path}
              onClick={() => go(entry.path)}
              onMouseEnter={() => setActiveIndex(i)}
              className={cn(
                'flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm',
                activeIndex === i ? 'bg-primary-50 text-primary-700' : 'text-ink'
              )}
            >
              <ArrowRight className="h-4 w-4 text-ink-muted" />
              <span className="flex-1">{entry.label}</span>
              <span className="text-xs text-ink-muted">{entry.section}</span>
            </button>
          ))}

          {/* Resultados da busca */}
          {query.trim().length >= 2 && (
            <>
              <p className="px-3 pb-1 pt-3 text-[11px] font-semibold uppercase tracking-wider text-ink-muted">
                {searching
                  ? 'Buscando...'
                  : results.length > 0
                    ? `Resultados (${results.length})`
                    : 'Nenhum resultado encontrado'}
              </p>
              {results.map((item, i) => (
                <button
                  key={`${item.type}-${item.id}`}
                  onClick={() => {
                    onClose();
                    if (item.type === 'project') go('/projects');
                    else if (item.type === 'agent') go('/agents');
                    else if (item.type === 'workflow') go('/workflows');
                    else if (item.type === 'knowledge') go('/knowledge-base');
                    else if (item.type === 'organization') go('/organizations');
                    else if (item.type === 'plugin') go('/plugins');
                    else go('/dashboard');
                  }}
                  onMouseEnter={() => setActiveIndex(filteredNav.length + i)}
                  className={cn(
                    'flex w-full items-start gap-3 rounded-lg px-3 py-2.5 text-left text-sm',
                    activeIndex === filteredNav.length + i
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-ink'
                  )}
                >
                  <FileText className="mt-0.5 h-4 w-4 shrink-0 text-ink-muted" />
                  <span className="min-w-0 flex-1">
                    <span className="block truncate font-medium">{item.title}</span>
                    <span className="block truncate text-xs text-ink-muted">{item.snippet}</span>
                  </span>
                  <span className="badge-neutral shrink-0">{item.type}</span>
                </button>
              ))}
            </>
          )}
        </div>

        <div className="flex items-center gap-4 border-t border-line bg-surface-alt px-4 py-2 text-[11px] text-ink-muted">
          <span className="flex items-center gap-1">
            <CornerDownLeft className="h-3 w-3" /> selecionar
          </span>
          <span>↑↓ navegar</span>
          <span className="ml-auto">Esc fechar</span>
        </div>
      </div>
    </div>
  );
}
