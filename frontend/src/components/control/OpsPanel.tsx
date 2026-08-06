"use client";

import { useCallback, useEffect, useState } from "react";
import { backupApi } from "@/api/backup";
import { costApi } from "@/api/cost";
import { pluginsApi } from "@/api/plugins";
import { featureFlagsApi } from "@/api/featureFlags";
import { notificationsApi } from "@/api/notifications";
import { dataApi } from "@/api/data";
import { workspaceApi } from "@/api/workspace";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";
import { ActionFeedback, ControlSection, errMsg, unwrapList, unwrapObj } from "./ControlSection";

function formatUSD(n: unknown): string {
  const v = Number(n ?? 0);
  if (!Number.isFinite(v)) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(v);
}

export function OpsPanel() {
  const [backups, setBackups] = useState<Record<string, unknown>[]>([]);
  const [cost, setCost] = useState<Record<string, unknown>>({});
  const [flags, setFlags] = useState<Record<string, unknown>[]>([]);
  const [plugins, setPlugins] = useState<Record<string, unknown>[]>([]);
  const [unread, setUnread] = useState(0);
  const [sessions, setSessions] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [wsName, setWsName] = useState("");

  const load = useCallback(async (showSpinner = true) => {
    if (showSpinner) setLoading(true);
    try {
      const [b, c, f, p, n, w] = await Promise.all([
        backupApi.list().catch(() => []),
        costApi.summary().catch(() => ({})),
        featureFlagsApi.list().catch(() => ({ flags: [] })),
        pluginsApi.installed().catch(() => []),
        notificationsApi.unreadCount().catch(() => ({ count: 0 })),
        workspaceApi.list().catch(() => []),
      ]);
      setBackups(unwrapList<Record<string, unknown>>(b));
      setCost(unwrapObj(c));
      setFlags(unwrapList<Record<string, unknown>>(f));
      setPlugins(unwrapList<Record<string, unknown>>(p));
      setUnread(Number(unwrapObj(n).count ?? 0));
      setSessions(unwrapList<Record<string, unknown>>(w));
    } catch (e) {
      setFeedback(`❌ ${errMsg(e)}`);
    } finally {
      if (showSpinner) setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const run = async (action: string, fn: () => Promise<unknown>, msg: string) => {
    setBusy(action);
    setFeedback(null);
    try {
      await fn();
      setFeedback(`✅ ${msg}`);
      await load(false);
    } catch (e) {
      setFeedback(`❌ ${errMsg(e)}`);
    } finally {
      setBusy(null);
    }
  };

  return (
    <ControlSection
      icon="🗄️"
      title="Operações"
      subtitle="Backups, custos, plugins, flags, notificações e workspaces"
      action={
        <Button variant="secondary" size="sm" onClick={() => load()} disabled={loading}>
          {loading ? "..." : "⟳"}
        </Button>
      }
    >
      {/* Backups + Custos */}
      <div className="grid gap-4 lg:grid-cols-2 mb-4">
        <div>
          <p className="mb-2 text-xs font-medium text-surface-400 uppercase tracking-wider">
            Backups
          </p>
          <div className="flex flex-wrap gap-2 mb-2">
            <Button variant="primary" size="sm" isLoading={busy === "bk-db"}
              onClick={() => run("bk-db", () => backupApi.database(), "Backup do banco criado")}>
              💾 Banco
            </Button>
            <Button variant="secondary" size="sm" isLoading={busy === "bk-files"}
              onClick={() => run("bk-files", () => backupApi.files(), "Backup de arquivos criado")}>
              📁 Arquivos
            </Button>
            <Button variant="secondary" size="sm" isLoading={busy === "bk-full"}
              onClick={() => run("bk-full", () => backupApi.full(), "Backup completo criado")}>
              🗄️ Completo
            </Button>
          </div>
          {backups.length > 0 && (
            <div className="max-h-24 overflow-y-auto space-y-1">
              {backups.slice(0, 4).map((b) => {
                const id = String(b.id ?? "");
                return (
                  <div key={id} className="flex items-center gap-2 text-xs">
                    <span className="text-surface-400">{String(b.kind ?? "backup")}</span>
                    <span className="min-w-0 flex-1 truncate font-mono text-surface-500">{String(b.path ?? id)}</span>
                    {b.size_bytes ? <span className="text-surface-400">{String(b.size_bytes)}B</span> : null}
                  </div>
                );
              })}
            </div>
          )}
          {backups.length === 0 && (
            <p className="text-xs text-surface-400">Nenhum backup encontrado</p>
          )}
        </div>

        <div>
          <p className="mb-2 text-xs font-medium text-surface-400 uppercase tracking-wider">
            Custos
          </p>
          <div className="grid grid-cols-2 gap-2">
            <div className="rounded-lg bg-surface-50 px-3 py-2 dark:bg-surface-800">
              <p className="text-[10px] text-surface-400 uppercase tracking-wider">Hoje</p>
              <p className="text-sm font-semibold text-surface-900 dark:text-surface-50">{formatUSD(cost.today_usd)}</p>
            </div>
            <div className="rounded-lg bg-surface-50 px-3 py-2 dark:bg-surface-800">
              <p className="text-[10px] text-surface-400 uppercase tracking-wider">Mês</p>
              <p className="text-sm font-semibold text-primary-600 dark:text-primary-400">{formatUSD(cost.month_usd ?? cost.total_usd)}</p>
            </div>
          </div>
          <Button variant="ghost" size="sm" className="mt-2" onClick={() => run("export", () => dataApi.export("json"), "Exportação de dados iniciada")}>
            📤 Exportar Dados
          </Button>
        </div>
      </div>

      {/* Flags + Plugins */}
      <div className="grid gap-4 lg:grid-cols-2 mb-4">
        <div>
          <p className="mb-2 text-xs font-medium text-surface-400 uppercase tracking-wider">
            Feature flags ({flags.length})
          </p>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {flags.length === 0 && (
              <p className="text-sm text-surface-400">Nenhuma flag configurada</p>
            )}
            {flags.slice(0, 8).map((fl) => {
              const name = String(fl.name ?? "");
              const enabled = fl.enabled === true || fl.enabled === "true";
              return (
                <div key={name} className="flex items-center gap-2 rounded-lg border border-surface-100 bg-surface-50/50 px-3 py-1.5 dark:border-surface-800 dark:bg-surface-800/50">
                  <span className="min-w-0 flex-1 truncate text-sm text-surface-900 dark:text-surface-50">{name}</span>
                  <Badge variant={enabled ? "success" : "default"} size="sm">{enabled ? "on" : "off"}</Badge>
                  <Button variant={enabled ? "ghost" : "primary"} size="sm" isLoading={busy === `fl-${name}`}
                    onClick={() => run(`fl-${name}`, () => featureFlagsApi.toggle(name), `Flag ${name} alternada`)}>
                    {enabled ? "⏸" : "▶"}
                  </Button>
                </div>
              );
            })}
          </div>
        </div>

        <div>
          <p className="mb-2 text-xs font-medium text-surface-400 uppercase tracking-wider">
            Plugins instalados ({plugins.length})
          </p>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {plugins.length === 0 && (
              <p className="text-sm text-surface-400">Nenhum plugin instalado</p>
            )}
            {plugins.slice(0, 8).map((p) => {
              const slug = String(p.slug ?? "");
              const enabled = p.enabled === true || p.enabled === "true";
              return (
                <div key={slug} className="flex items-center gap-2 rounded-lg border border-surface-100 bg-surface-50/50 px-3 py-1.5 dark:border-surface-800 dark:bg-surface-800/50">
                  <span className="min-w-0 flex-1 truncate text-sm text-surface-900 dark:text-surface-50">{slug}</span>
                  <Badge variant={enabled ? "success" : "default"} size="sm">{enabled ? "on" : "off"}</Badge>
                  {enabled ? (
                    <Button variant="ghost" size="sm" isLoading={busy === `pd-${slug}`}
                      onClick={() => run(`pd-${slug}`, () => pluginsApi.disable(slug), `Plugin ${slug} desativado`)}>
                      ⏸
                    </Button>
                  ) : (
                    <Button variant="primary" size="sm" isLoading={busy === `pe-${slug}`}
                      onClick={() => run(`pe-${slug}`, () => pluginsApi.enable(slug), `Plugin ${slug} ativado`)}>
                      ▶
                    </Button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Workspaces + Notificações */}
      <div className="grid gap-4 lg:grid-cols-2">
        <div>
          <p className="mb-2 text-xs font-medium text-surface-400 uppercase tracking-wider">
            Workspaces ({sessions.length})
          </p>
          <div className="flex gap-2 mb-2">
            <input
              value={wsName}
              onChange={(e) => setWsName(e.target.value)}
              placeholder="Nome da sessão..."
              className="min-w-0 flex-1 rounded-lg border border-surface-300 bg-white px-3 py-1.5 text-sm text-surface-900 dark:border-surface-600 dark:bg-surface-900 dark:text-surface-100"
            />
            <Button variant="primary" size="sm" isLoading={busy === "ws-new"} disabled={!wsName.trim()}
              onClick={() => run("ws-new", () => workspaceApi.create({ name: wsName.trim() }), `Sessão ${wsName.trim()} criada`).then(() => setWsName(""))}>
              ➕
            </Button>
          </div>
          {sessions.length > 0 && (
            <div className="max-h-24 overflow-y-auto space-y-1">
              {sessions.slice(0, 4).map((s) => {
                const id = String(s.id ?? "");
                return (
                  <div key={id} className="flex items-center gap-2 text-xs">
                    <Badge variant={s.status === "active" ? "success" : "default"} size="sm">{String(s.status ?? "idle")}</Badge>
                    <span className="min-w-0 flex-1 truncate text-surface-700 dark:text-surface-300">{String(s.name ?? id)}</span>
                  </div>
                );
              })}
            </div>
          )}
          {sessions.length === 0 && <p className="text-xs text-surface-400">Nenhuma sessão ativa</p>}
        </div>

        <div>
          <p className="mb-2 text-xs font-medium text-surface-400 uppercase tracking-wider">
            Notificações
          </p>
          <div className="flex items-center gap-2">
            <Badge variant={unread > 0 ? "warning" : "success"}>{unread} não lidas</Badge>
            <Button variant="secondary" size="sm" isLoading={busy === "ntf-read"}
              onClick={() => run("ntf-read", () => notificationsApi.markAllRead(), "Todas as notificações marcadas como lidas")}>
              ✓ Marcar lidas
            </Button>
          </div>
        </div>
      </div>

      <ActionFeedback message={feedback} />
    </ControlSection>
  );
}
