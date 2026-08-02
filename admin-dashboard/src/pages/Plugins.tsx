import { useState } from 'react';
import { Puzzle, Download, Power, Trash2, Star, Loader2, CheckCircle2 } from 'lucide-react';
import { usePluginMarketplace, useInstallPlugin, useUninstallPlugin, useTogglePlugin } from '../hooks/usePlugins';
import type { PluginRegistryEntry } from '../types/api';
import { cn } from '../lib/utils';

/** Página de plugins — marketplace + instalados com ações reais. */
export function Plugins() {
  const { featured, installed, installedSlugs, isLoading } = usePluginMarketplace();
  const installPlugin = useInstallPlugin();
  const uninstallPlugin = useUninstallPlugin();
  const togglePlugin = useTogglePlugin();

  const [tab, setTab] = useState<'featured' | 'installed'>('featured');

  const busy = installPlugin.isPending || uninstallPlugin.isPending || togglePlugin.isPending;

  const onInstall = async (plugin: PluginRegistryEntry) => {
    try {
      await installPlugin.mutateAsync({ slug: plugin.slug });
    } catch {
      // silencioso
    }
  };

  const onUninstall = async (slug: string) => {
    if (!window.confirm(`Desinstalar o plugin "${slug}"?`)) return;
    try {
      await uninstallPlugin.mutateAsync(slug);
    } catch {
      // silencioso
    }
  };

  const onToggle = async (slug: string, enabled: boolean) => {
    try {
      await togglePlugin.mutateAsync({ slug, enable: !enabled });
    } catch {
      // silencioso
    }
  };

  const isInstalled = (slug: string) => installedSlugs.has(slug);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Plugins</h1>
          <p className="page-subtitle">
            Estenda o SuperDev com plugins do marketplace ({installed.length} instalados)
          </p>
        </div>
        <div className="flex rounded-lg border border-line bg-surface p-0.5">
          <button
            onClick={() => setTab('featured')}
            className={cn('rounded-md px-3 py-1.5 text-sm font-medium transition', tab === 'featured' ? 'bg-primary-600 text-white shadow-sm' : 'text-ink-muted hover:text-ink')}
          >
            Em destaque
          </button>
          <button
            onClick={() => setTab('installed')}
            className={cn('rounded-md px-3 py-1.5 text-sm font-medium transition', tab === 'installed' ? 'bg-primary-600 text-white shadow-sm' : 'text-ink-muted hover:text-ink')}
          >
            Instalados ({installed.length})
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="card p-5">
              <div className="skeleton h-4 w-2/3" />
              <div className="skeleton mt-3 h-3 w-1/2" />
              <div className="skeleton mt-3 h-3 w-1/3" />
            </div>
          ))}
        </div>
      ) : tab === 'featured' ? (
        featured.length === 0 ? (
          <div className="card">
            <div className="empty-state">
              <Puzzle className="h-8 w-8 text-ink-muted" />
              <p className="empty-title">Marketplace vazio</p>
              <p className="empty-hint">Os plugins em destaque aparecerão aqui.</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {featured.map((plugin) => {
              const isInst = isInstalled(plugin.slug);
              return (
                <div key={plugin.slug} className="card card-hover flex flex-col p-5">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-fuchsia-50 text-fuchsia-600 dark:bg-fuchsia-500/10 dark:text-fuchsia-400">
                        <Puzzle className="h-5 w-5" />
                      </div>
                      <div className="min-w-0">
                        <p className="truncate font-semibold text-ink">{plugin.name}</p>
                        <p className="text-xs text-ink-muted">
                          {plugin.author} · v{plugin.version}
                        </p>
                      </div>
                    </div>
                    {plugin.is_official && <span className="badge-info shrink-0">Oficial</span>}
                  </div>

                  <p className="mt-3 line-clamp-2 min-h-[2.5rem] flex-1 text-sm text-ink-muted">
                    {plugin.description}
                  </p>

                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {(plugin.tags ?? []).slice(0, 3).map((tag) => (
                      <span key={tag} className="badge-neutral">{tag}</span>
                    ))}
                  </div>

                  <div className="mt-4 flex items-center justify-between border-t border-line pt-3">
                    <div className="flex items-center gap-3 text-xs text-ink-muted">
                      <span className="flex items-center gap-1">
                        <Download className="h-3.5 w-3.5" /> {plugin.downloads.toLocaleString('pt-BR')}
                      </span>
                      <span className="flex items-center gap-1">
                        <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" /> {plugin.rating.toFixed(1)}
                      </span>
                    </div>
                    {isInst ? (
                      <span className="badge-success">
                        <CheckCircle2 className="h-3 w-3" /> Instalado
                      </span>
                    ) : (
                      <button
                        onClick={() => void onInstall(plugin)}
                        disabled={busy}
                        className="btn-primary btn-sm"
                      >
                        {busy && installPlugin.isPending && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                        Instalar
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )
      ) : installed.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <Puzzle className="h-8 w-8 text-ink-muted" />
            <p className="empty-title">Nenhum plugin instalado</p>
            <p className="empty-hint">Instale plugins pela aba "Em destaque".</p>
          </div>
        </div>
      ) : (
        <div className="card">
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Plugin</th>
                  <th>Versão</th>
                  <th>Status</th>
                  <th className="text-right">Ações</th>
                </tr>
              </thead>
              <tbody>
                {installed.map((plugin) => {
                  const enabled = plugin.status === 'enabled';
                  return (
                    <tr key={plugin.slug}>
                      <td>
                        <div className="flex items-center gap-3">
                          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-fuchsia-50 text-fuchsia-600 dark:bg-fuchsia-500/10 dark:text-fuchsia-400">
                            <Puzzle className="h-4 w-4" />
                          </div>
                          <div>
                            <p className="font-medium text-ink">{plugin.name}</p>
                            <p className="text-xs text-ink-muted">{plugin.slug}</p>
                          </div>
                        </div>
                      </td>
                      <td className="text-ink-muted">{plugin.version}</td>
                      <td>
                        <span className={cn('badge', enabled ? 'badge-active' : 'badge-neutral')}>
                          {enabled ? 'Ativo' : 'Desativado'}
                        </span>
                      </td>
                      <td>
                        <div className="flex justify-end gap-1">
                          <button
                            onClick={() => void onToggle(plugin.slug, enabled)}
                            disabled={busy}
                            className={cn('btn-icon', enabled ? 'btn-ghost' : 'btn-primary')}
                            title={enabled ? 'Desativar' : 'Ativar'}
                          >
                            {busy && togglePlugin.isPending ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <Power className="h-4 w-4" />
                            )}
                          </button>
                          <button
                            onClick={() => void onUninstall(plugin.slug)}
                            disabled={busy}
                            className="btn-icon btn-ghost hover:!bg-danger-50 hover:!text-danger-600"
                            title="Desinstalar"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default Plugins;
