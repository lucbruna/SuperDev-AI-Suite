"use client";

import { useCallback, useEffect, useState } from "react";
import { scannersApi } from "@/api/scanners";
import { buildersApi } from "@/api/builders";
import { harnessApi } from "@/api/harness";
import { verificationApi } from "@/api/verification";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";
import { ActionFeedback, ControlSection, errMsg, unwrapList, unwrapObj } from "./ControlSection";

export function AutomationPanel() {
  const [scanners, setScanners] = useState<Record<string, unknown>[]>([]);
  const [builders, setBuilders] = useState<Record<string, unknown>[]>([]);
  const [harness, setHarness] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [verifyCode, setVerifyCode] = useState("");
  const [verifyLang, setVerifyLang] = useState("python");

  const load = useCallback(async (showSpinner = true) => {
    if (showSpinner) setLoading(true);
    try {
      const [s, b, h] = await Promise.all([
        scannersApi.list(),
        buildersApi.list(),
        harnessApi.status(),
      ]);
      setScanners(unwrapList<Record<string, unknown>>(s));
      setBuilders(unwrapList<Record<string, unknown>>(b));
      setHarness(unwrapObj(h));
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

  const harnessStatus = String(harness.status ?? "unknown");

  return (
    <ControlSection
      icon="⚙️"
      title="Automação"
      subtitle="Scanners, builders, harness e verificação de código"
      action={
        <Button variant="secondary" size="sm" onClick={() => load()} disabled={loading}>
          {loading ? "..." : "⟳"}
        </Button>
      }
    >
      {/* Ações em massa */}
      <div className="flex flex-wrap gap-2 mb-4">
        <Badge variant={harnessStatus === "running" ? "success" : "warning"} dot>
          Harness: {harnessStatus}
        </Badge>
        <Badge variant="info">{scanners.length} scanners</Badge>
        <Badge variant="info">{builders.length} builders</Badge>
        <div className="ml-auto flex flex-wrap gap-2">
          <Button
            variant="primary"
            size="sm"
            isLoading={busy === "scan-all"}
            onClick={() => run("scan-all", () => scannersApi.scanAll(), "Scan de todos os scanners disparado")}
          >
            🔍 Scan All
          </Button>
          <Button
            variant="primary"
            size="sm"
            isLoading={busy === "build-all"}
            onClick={() => run("build-all", () => buildersApi.buildAll(), "Build de todos os builders disparado")}
          >
            🏗️ Build All
          </Button>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {/* Scanners */}
        <div>
          <p className="mb-2 text-xs font-medium text-surface-400 uppercase tracking-wider">
            Scanners de segurança
          </p>
          <div className="space-y-2">
            {scanners.length === 0 && (
              <p className="text-sm text-surface-400">Nenhum scanner registrado</p>
            )}
            {scanners.slice(0, 5).map((s) => {
              const id = String(s.id ?? s.name ?? "");
              const available = s.available !== false;
              return (
                <div key={id} className="flex items-center gap-2 rounded-lg border border-surface-100 bg-surface-50/50 px-3 py-2 dark:border-surface-800 dark:bg-surface-800/50">
                  <span className="min-w-0 flex-1 truncate text-sm text-surface-900 dark:text-surface-50">
                    {String(s.name ?? id)}
                  </span>
                  <Badge variant={available ? "success" : "default"} size="sm">
                    {available ? "disponível" : "indisponível"}
                  </Badge>
                  <Button variant="secondary" size="sm" isLoading={busy === `scan-${id}`}
                    onClick={() => run(`scan-${id}`, () => scannersApi.scanOne(id), `Scan ${s.name ?? id} concluído`)}>
                    🔍
                  </Button>
                </div>
              );
            })}
          </div>
        </div>

        {/* Builders */}
        <div>
          <p className="mb-2 text-xs font-medium text-surface-400 uppercase tracking-wider">
            Builders
          </p>
          <div className="space-y-2">
            {builders.length === 0 && (
              <p className="text-sm text-surface-400">Nenhum builder registrado</p>
            )}
            {builders.slice(0, 5).map((b) => {
              const id = String(b.id ?? b.name ?? "");
              const available = b.available !== false;
              return (
                <div key={id} className="flex items-center gap-2 rounded-lg border border-surface-100 bg-surface-50/50 px-3 py-2 dark:border-surface-800 dark:bg-surface-800/50">
                  <span className="min-w-0 flex-1 truncate text-sm text-surface-900 dark:text-surface-50">
                    {String(b.name ?? id)}
                  </span>
                  <Badge variant={available ? "success" : "default"} size="sm">
                    {available ? "disponível" : "indisponível"}
                  </Badge>
                  <Button variant="secondary" size="sm" isLoading={busy === `build-${id}`}
                    onClick={() => run(`build-${id}`, () => buildersApi.buildOne(id), `Build ${b.name ?? id} disparado`)}>
                    🏗️
                  </Button>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Verificação de código */}
      <div className="mt-4 rounded-lg border border-surface-200 p-3 dark:border-surface-700">
        <p className="mb-2 text-xs font-medium text-surface-400 uppercase tracking-wider">
          Verificação de código
        </p>
        <div className="flex flex-wrap gap-2">
          <select
            value={verifyLang}
            onChange={(e) => setVerifyLang(e.target.value)}
            className="rounded-lg border border-surface-300 bg-white px-2 py-1.5 text-sm text-surface-900 dark:border-surface-600 dark:bg-surface-900 dark:text-surface-100"
          >
            {["python", "javascript", "typescript", "go", "rust"].map((l) => (
              <option key={l} value={l}>{l}</option>
            ))}
          </select>
          <input
            value={verifyCode}
            onChange={(e) => setVerifyCode(e.target.value)}
            placeholder="Trecho de código para verificar..."
            className="min-w-0 flex-1 rounded-lg border border-surface-300 bg-white px-3 py-1.5 text-sm text-surface-900 dark:border-surface-600 dark:bg-surface-900 dark:text-surface-100"
          />
          <Button
            variant="secondary"
            size="sm"
            isLoading={busy === "verify"}
            disabled={!verifyCode.trim()}
            onClick={() =>
              run("verify", () => verificationApi.verify({ task_description: verifyCode, language: verifyLang }), "Verificação concluída")
            }
          >
            ✅ Verificar
          </Button>
          <Button
            variant="ghost"
            size="sm"
            isLoading={busy === "review"}
            disabled={!verifyCode.trim()}
            onClick={() =>
              run("review", () => verificationApi.review({ code: verifyCode, language: verifyLang }), "Review concluído")
            }
          >
            🔎 Review
          </Button>
        </div>
      </div>

      <ActionFeedback message={feedback} />
    </ControlSection>
  );
}
