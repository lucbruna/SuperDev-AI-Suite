import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { pluginsApi, withFallback } from '../services/api';
import type { PluginInstalled, PluginRegistryEntry } from '../types/api';

export const pluginKeys = {
  all: ['plugins'] as const,
  registry: ['plugins', 'registry'] as const,
  installed: ['plugins', 'installed'] as const,
};

/** Catálogo de plugins (defensivo: [] em falha). */
export function usePluginRegistry() {
  const query = useQuery({
    queryKey: pluginKeys.registry,
    queryFn: () => withFallback(pluginsApi.listRegistry(), []),
  });
  return { ...query, registry: query.data ?? [] };
}

/** Plugins instalados (defensivo: [] em falha). */
export function useInstalledPlugins() {
  const query = useQuery({
    queryKey: pluginKeys.installed,
    queryFn: () => withFallback(pluginsApi.listInstalled(), []),
  });
  return { ...query, installed: query.data ?? [] };
}

export function useInstallPlugin() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ slug, config }: { slug: string; config?: Record<string, unknown> }) =>
      pluginsApi.install(slug, config),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: pluginKeys.all }),
  });
}

export function useUninstallPlugin() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (slug: string) => pluginsApi.uninstall(slug),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: pluginKeys.all }),
  });
}

export function useTogglePlugin() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ slug, enable }: { slug: string; enable: boolean }) =>
      enable ? pluginsApi.enable(slug) : pluginsApi.disable(slug),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: pluginKeys.all }),
  });
}

/** Agrega: instalados + os 8 mais populares do catálogo. */
export function usePluginMarketplace() {
  const registryQuery = usePluginRegistry();
  const installedQuery = useInstalledPlugins();
  const installedSlugs = new Set((installedQuery.installed as PluginInstalled[]).map((p) => p.slug));

  const featured: PluginRegistryEntry[] = (registryQuery.registry as PluginRegistryEntry[])
    .slice()
    .sort((a, b) => b.downloads - a.downloads)
    .slice(0, 8);

  return {
    registry: registryQuery.registry,
    installed: installedQuery.installed,
    featured,
    installedSlugs,
    isLoading: registryQuery.isLoading || installedQuery.isLoading,
    isError: registryQuery.isError || installedQuery.isError,
  };
}
