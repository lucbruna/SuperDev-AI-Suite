"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { aiApi, type AiModuleInfo } from "@/api/ai";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";
import { ActionFeedback, ControlSection, errMsg, unwrapList, unwrapObj } from "./ControlSection";

const moduleIcon: Record<string, string> = {
  orchestrator: "🎯",
  data_platform: "📊",
  erp: "🏭",
  business_intelligence: "📈",
  customer_experience: "👥",
  verification: "✅",
  knowledge: "🧠",
  ai_tools: "🔧",
  cybersecurity: "🛡️",
};

export function AiModulesPanel() {
  const [modules, setModules] = useState<AiModuleInfo[]>([]);
  const [stats, setStats] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  const load = useCallback(async (showSpinner = true) => {
    if (showSpinner) setLoading(true);
    try {
      const [m, s] = await Promise.all([aiApi.modules(), aiApi.stats()]);
      setModules(unwrapList<AiModuleInfo>(m));
      setStats(unwrapObj(s));
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

  const keys = Object.keys(stats);
  const enabledCount = modules.filter((m) => m.enabled !== false).length;

  return (
    <ControlSection
      icon="🧠"
      title="Módulos de IA"
      subtitle="Status ao vivo de todos os módulos (backend /ai)"
      action={
        <Button variant="secondary" size="sm" onClick={() => load()} disabled={loading}>
          {loading ? "..." : "⟳"}
        </Button>
      }
    >
      <div className="flex flex-wrap items-center gap-2 mb-4">
        <Badge variant="primary">{modules.length} módulos</Badge>
        <Badge variant="success">{enabledCount} ativos</Badge>
        {keys.length > 0 && <Badge variant="info">{keys.length} métricas</Badge>}
      </div>

      {modules.length === 0 ? (
        <p className="text-center text-sm text-surface-400 py-6">
          Nenhum módulo de IA reportado pelo backend
        </p>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {modules.map((m) => {
            const name = String(m.name ?? "");
            const st = String(m.status ?? "unknown");
            return (
              <Link key={name} href="/agents" className="group">
                <div className="flex flex-col items-center gap-2 rounded-xl border border-surface-200 p-4 transition-all hover:border-primary-300 hover:shadow-sm dark:border-surface-700 dark:hover:border-primary-700">
                  <span className="text-2xl">
                    {moduleIcon[name.toLowerCase()] ?? "🤖"}
                  </span>
                  <p className="text-xs font-semibold text-surface-900 dark:text-surface-50 text-center leading-tight">
                    {name}
                  </p>
                  {m.description && (
                    <p className="text-[10px] text-surface-400 text-center leading-tight line-clamp-2">
                      {String(m.description)}
                    </p>
                  )}
                  <Badge
                    variant={st === "running" || st === "healthy" || st === "ok" ? "success" : st === "error" || st === "failed" ? "danger" : "warning"}
                    size="sm"
                    dot
                  >
                    {st}
                  </Badge>
                </div>
              </Link>
            );
          })}
        </div>
      )}

      {keys.length > 0 && (
        <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-2">
          {keys.slice(0, 8).map((k) => (
            <div key={k} className="rounded-lg bg-surface-50 px-3 py-2 dark:bg-surface-800">
              <p className="text-[10px] text-surface-400 uppercase tracking-wider truncate">{k}</p>
              <p className="text-sm font-semibold text-surface-900 dark:text-surface-50 truncate">
                {String(stats[k] ?? "—")}
              </p>
            </div>
          ))}
        </div>
      )}

      <ActionFeedback message={feedback} />
    </ControlSection>
  );
}
