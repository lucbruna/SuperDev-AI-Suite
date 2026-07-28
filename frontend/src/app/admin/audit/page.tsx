"use client";

import { useState } from "react";

export default function AuditPage() {
  const [activeTab, setActiveTab] = useState<"logs" | "compliance" | "policies">("logs");
  const [severity, setSeverity] = useState("all");

  const logs = [
    { id: "1", action: "USER_LOGIN", user: "admin@superdev.ai", resource: "auth", timestamp: "2026-07-28T10:00:00Z", severity: "info", success: true },
    { id: "2", action: "WORKFLOW_EXECUTE", user: "dev@superdev.ai", resource: "workflow:ci-cd", timestamp: "2026-07-28T09:45:00Z", severity: "info", success: true },
    { id: "3", action: "AGENT_CREATE", user: "dev@superdev.ai", resource: "agent:architect", timestamp: "2026-07-28T09:30:00Z", severity: "info", success: true },
    { id: "4", action: "PERMISSION_DENIED", user: "guest@superdev.ai", resource: "admin:settings", timestamp: "2026-07-28T09:15:00Z", severity: "warning", success: false },
    { id: "5", action: "BACKUP_CREATE", user: "system", resource: "backup:auto", timestamp: "2026-07-28T08:00:00Z", severity: "info", success: true },
    { id: "6", action: "COMPLIANCE_CHECK", user: "system", resource: "compliance:soc2", timestamp: "2026-07-28T07:00:00Z", severity: "info", success: true },
    { id: "7", action: "API_KEY_ROTATED", user: "admin@superdev.ai", resource: "apikey:prod", timestamp: "2026-07-27T22:00:00Z", severity: "critical", success: true },
  ];

  const complianceFrameworks = [
    { name: "SOC2", status: "compliant", passed: 12, failed: 0, lastCheck: "2026-07-28" },
    { name: "GDPR", status: "compliant", passed: 8, failed: 0, lastCheck: "2026-07-28" },
    { name: "HIPAA", status: "non-compliant", passed: 6, failed: 2, lastCheck: "2026-07-27" },
  ];

  const severityColor = (s: string) => {
    if (s === "critical") return "bg-red-100 text-red-700";
    if (s === "warning") return "bg-yellow-100 text-yellow-700";
    return "bg-blue-100 text-blue-700";
  };

  const filtered = severity === "all" ? logs : logs.filter((l) => l.severity === severity);

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950">
      <header className="border-b bg-white dark:border-surface-700 dark:bg-surface-900">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <h1 className="text-xl font-bold text-primary-600">SuperDev</h1>
          <nav className="flex items-center gap-4">
            <a href="/admin/users" className="text-sm font-medium text-surface-600 hover:text-surface-900">Admin</a>
            <a href="/admin/audit" className="text-sm font-medium text-primary-600">Audit</a>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Audit Trail</h2>
            <p className="mt-1 text-sm text-surface-600">All actions logged for compliance and security</p>
          </div>
          <div className="flex gap-2">
            <button className="rounded-lg bg-surface-200 px-3 py-1.5 text-sm text-surface-700 dark:bg-surface-700 dark:text-surface-300">Export CSV</button>
            <button className="rounded-lg bg-surface-200 px-3 py-1.5 text-sm text-surface-700 dark:bg-surface-700 dark:text-surface-300">Export JSON</button>
          </div>
        </div>

        <div className="mt-4 flex gap-2">
          {(["logs", "compliance", "policies"] as const).map((tab) => (
            <button key={tab} onClick={() => setActiveTab(tab)} className={`rounded-lg px-4 py-2 text-sm font-medium ${activeTab === tab ? "bg-primary-600 text-white" : "bg-surface-200 text-surface-600 dark:bg-surface-700 dark:text-surface-400"}`}>
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
          {activeTab === "logs" && (
            <div className="ml-auto flex gap-2">
              <select value={severity} onChange={(e) => setSeverity(e.target.value)} className="rounded-lg border border-surface-300 bg-white px-3 py-1.5 text-sm dark:border-surface-600 dark:bg-surface-800">
                <option value="all">All Severities</option>
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="critical">Critical</option>
              </select>
              <input type="text" placeholder="Search audit logs..." className="rounded-lg border border-surface-300 bg-white px-3 py-1.5 text-sm dark:border-surface-600 dark:bg-surface-800" />
            </div>
          )}
        </div>

        {activeTab === "logs" && (
          <div className="mt-4 overflow-x-auto rounded-xl border bg-white dark:border-surface-700 dark:bg-surface-900">
            <table className="w-full text-left text-sm">
              <thead className="border-b bg-surface-50 dark:border-surface-700 dark:bg-surface-800">
                <tr>
                  <th className="px-4 py-3 font-medium text-surface-600">Action</th>
                  <th className="px-4 py-3 font-medium text-surface-600">User</th>
                  <th className="px-4 py-3 font-medium text-surface-600">Resource</th>
                  <th className="px-4 py-3 font-medium text-surface-600">Timestamp</th>
                  <th className="px-4 py-3 font-medium text-surface-600">Severity</th>
                  <th className="px-4 py-3 font-medium text-surface-600">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y dark:divide-surface-700">
                {filtered.map((log) => (
                  <tr key={log.id} className="hover:bg-surface-50 dark:hover:bg-surface-800/50">
                    <td className="px-4 py-3 font-mono text-xs text-surface-700">{log.action}</td>
                    <td className="px-4 py-3 text-surface-700">{log.user}</td>
                    <td className="px-4 py-3 font-mono text-xs text-surface-500">{log.resource}</td>
                    <td className="px-4 py-3 text-xs text-surface-400">{new Date(log.timestamp).toLocaleString()}</td>
                    <td className="px-4 py-3"><span className={`rounded px-2 py-0.5 text-xs font-medium ${severityColor(log.severity)}`}>{log.severity}</span></td>
                    <td className="px-4 py-3">{log.success ? <span className="text-green-600">✓</span> : <span className="text-red-600">✗</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === "compliance" && (
          <div className="mt-4 space-y-4">
            {complianceFrameworks.map((f) => (
              <div key={f.name} className="rounded-xl border bg-white p-5 dark:border-surface-700 dark:bg-surface-900">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${f.status === "compliant" ? "bg-green-100 text-green-600" : "bg-red-100 text-red-600"}`}>
                      {f.status === "compliant" ? "✓" : "✗"}
                    </div>
                    <div>
                      <h3 className="font-semibold text-surface-900 dark:text-surface-50">{f.name}</h3>
                      <p className="text-xs text-surface-500">Last check: {f.lastCheck}</p>
                    </div>
                  </div>
                  <span className={`rounded-full px-3 py-1 text-xs font-medium ${f.status === "compliant" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                    {f.status === "compliant" ? "Compliant" : "Non-Compliant"}
                  </span>
                </div>
                <div className="mt-4 flex gap-4 text-sm">
                  <span className="text-surface-600">Passed: <strong className="text-green-600">{f.passed}</strong></span>
                  <span className="text-surface-600">Failed: <strong className="text-red-600">{f.failed}</strong></span>
                  <span className="text-surface-600">Total: <strong>{f.passed + f.failed}</strong></span>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === "policies" && (
          <div className="mt-4 rounded-xl border bg-white p-6 dark:border-surface-700 dark:bg-surface-900">
            <h3 className="text-lg font-bold text-surface-900 dark:text-surface-50">Retention Policies</h3>
            <div className="mt-4 space-y-3">
              {[
                { name: "Default", retention: "90 days", access: "Internal", maxEntries: 10000 },
                { name: "Security Events", retention: "1 year", access: "Restricted", maxEntries: 50000 },
                { name: "Compliance", retention: "3 years", access: "Confidential", maxEntries: 100000 },
                { name: "User Activity", retention: "30 days", access: "Internal", maxEntries: 5000 },
              ].map((p) => (
                <div key={p.name} className="flex items-center justify-between rounded-lg bg-surface-50 p-3 dark:bg-surface-800">
                  <div>
                    <p className="font-medium text-surface-900 dark:text-surface-50">{p.name}</p>
                    <p className="text-xs text-surface-500">Retention: {p.retention} | Access: {p.access} | Max: {p.maxEntries.toLocaleString()}</p>
                  </div>
                  <button className="rounded bg-surface-200 px-3 py-1 text-xs text-surface-600 dark:bg-surface-700">Edit</button>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}