"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/DashboardLayout";

export default function AuditPage() {
  const [activeTab, setActiveTab] = useState<"logs" | "compliance" | "policies">("logs");
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/admin/audit/logs")
      .then((r) => r.json())
      .then((d) => setLogs(Array.isArray(d) ? d : d.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <DashboardLayout>
      <h1 className="mb-6 text-2xl font-bold text-surface-900 dark:text-surface-50">Auditoria</h1>

      <div className="mb-4 flex gap-2">
        {(["logs", "compliance", "policies"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`rounded-lg px-4 py-2 text-sm font-medium ${
              activeTab === tab
                ? "bg-primary-600 text-white"
                : "bg-surface-200 text-surface-600 dark:bg-surface-700 dark:text-surface-400"
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {activeTab === "logs" && (
        <div className="rounded-xl border bg-white shadow-sm dark:border-surface-700 dark:bg-surface-900">
          {loading ? (
            <p className="p-6 text-surface-400">Carregando...</p>
          ) : (
            <table className="w-full text-left text-sm">
              <thead className="border-b dark:border-surface-700">
                <tr className="bg-surface-50 dark:bg-surface-800">
                  <th className="px-4 py-3 font-medium text-surface-600">Ação</th>
                  <th className="px-4 py-3 font-medium text-surface-600">Usuário</th>
                  <th className="px-4 py-3 font-medium text-surface-600">Recurso</th>
                  <th className="px-4 py-3 font-medium text-surface-600">Data</th>
                </tr>
              </thead>
              <tbody className="divide-y dark:divide-surface-700">
                {logs.map((log: any, i: number) => (
                  <tr key={log.id || i} className="hover:bg-surface-50 dark:hover:bg-surface-800/50">
                    <td className="px-4 py-3 font-mono text-xs text-surface-700">{log.action}</td>
                    <td className="px-4 py-3 text-surface-700">{log.user}</td>
                    <td className="px-4 py-3 text-surface-500">{log.resource}</td>
                    <td className="px-4 py-3 text-xs text-surface-400">
                      {log.timestamp ? new Date(log.timestamp).toLocaleString() : "-"}
                    </td>
                  </tr>
                ))}
                {logs.length === 0 && (
                  <tr><td colSpan={4} className="px-4 py-8 text-center text-surface-400">Nenhum log encontrado</td></tr>
                )}
              </tbody>
            </table>
          )}
        </div>
      )}

      {activeTab === "compliance" && (
        <div className="rounded-xl border bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900">
          <p className="text-surface-500">Nenhum framework de compliance configurado.</p>
        </div>
      )}

      {activeTab === "policies" && (
        <div className="rounded-xl border bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900">
          <p className="text-surface-500">Nenhuma política de retenção configurada.</p>
        </div>
      )}
    </DashboardLayout>
  );
}
