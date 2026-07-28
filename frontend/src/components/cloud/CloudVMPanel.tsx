"use client";

import { useState, useEffect } from "react";

interface VM {
  id: string;
  name: string;
  provider: string;
  region: string;
  spec: { cpu: number; memory_gb: number; disk_gb: number };
  status: string;
  ip: string | null;
  agent_id: string | null;
  created_at: string;
}

export function CloudVMPanel() {
  const [vms, setVms] = useState<VM[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [vmName, setVmName] = useState("");
  const [creating, setCreating] = useState(false);

  const refresh = async () => {
    try {
      const [vmsRes, statsRes] = await Promise.all([
        fetch("/api/cloud/vms"),
        fetch("/api/cloud/stats"),
      ]);
      setVms((await vmsRes.json()).vms || []);
      setStats(await statsRes.json());
    } catch {}
    setLoading(false);
  };

  useEffect(() => { refresh(); }, []);

  const createVM = async () => {
    if (!vmName.trim()) return;
    setCreating(true);
    try {
      await fetch(`/api/cloud/vms?name=${encodeURIComponent(vmName)}`, { method: "POST" });
      setVmName("");
      await refresh();
    } catch {}
    setCreating(false);
  };

  const action = async (id: string, action: string) => {
    try {
      await fetch(`/api/cloud/vms/${id}/${action}`, { method: "POST" });
      await refresh();
    } catch {}
  };

  const statusColor = (s: string) => {
    const colors: Record<string, string> = {
      running: "bg-green-500", occupied: "bg-blue-500", stopped: "bg-red-500",
      provisioning: "bg-yellow-500 animate-pulse", stopping: "bg-orange-500",
    };
    return colors[s] || "bg-surface-300";
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-4 gap-3">
        <div className="rounded-xl border bg-white p-3 dark:border-surface-700 dark:bg-surface-900">
          <p className="text-[10px] text-surface-500">Total VMs</p>
          <p className="text-lg font-bold text-surface-900 dark:text-surface-50">{stats?.total || 0}</p>
        </div>
        <div className="rounded-xl border bg-white p-3 dark:border-surface-700 dark:bg-surface-900">
          <p className="text-[10px] text-surface-500">Running</p>
          <p className="text-lg font-bold text-green-500">{stats?.by_status?.running || 0}</p>
        </div>
        <div className="rounded-xl border bg-white p-3 dark:border-surface-700 dark:bg-surface-900">
          <p className="text-[10px] text-surface-500">Occupied</p>
          <p className="text-lg font-bold text-blue-500">{stats?.by_status?.occupied || 0}</p>
        </div>
        <div className="rounded-xl border bg-white p-3 dark:border-surface-700 dark:bg-surface-900">
          <p className="text-[10px] text-surface-500">Provider</p>
          <p className="text-lg font-bold text-surface-900 dark:text-surface-50">{stats?.provider || "N/A"}</p>
        </div>
      </div>

      <div className="flex gap-2">
        <input value={vmName} onChange={(e) => setVmName(e.target.value)} onKeyDown={(e) => e.key === "Enter" && createVM()} placeholder="New VM name..." className="flex-1 rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100" />
        <button onClick={createVM} disabled={creating || !vmName.trim()} className="rounded-lg bg-primary-600 px-4 py-2 text-xs font-medium text-white hover:bg-primary-700 disabled:opacity-40">
          {creating ? "Creating..." : "Create VM"}
        </button>
      </div>

      <div className="rounded-xl border dark:border-surface-700">
        {loading ? (
          <div className="flex items-center justify-center p-8"><div className="h-6 w-6 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" /></div>
        ) : vms.length === 0 ? (
          <div className="p-8 text-center text-xs text-surface-400">No VMs yet. Create one to get started.</div>
        ) : (
          <div className="divide-y dark:divide-surface-700">
            {vms.map((vm) => (
              <div key={vm.id} className="flex items-center justify-between px-4 py-3">
                <div className="flex items-center gap-3">
                  <div className={`h-2.5 w-2.5 rounded-full ${statusColor(vm.status)}`} />
                  <div>
                    <p className="text-xs font-medium text-surface-900 dark:text-surface-50">{vm.name}</p>
                    <p className="text-[10px] text-surface-500">{vm.ip || "no ip"} · {vm.spec.cpu}vCPU · {vm.spec.memory_gb}GB</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="rounded bg-surface-100 px-2 py-0.5 text-[9px] text-surface-600 dark:bg-surface-700 dark:text-surface-300">{vm.provider}</span>
                  <span className={`rounded-full px-2 py-0.5 text-[9px] ${vm.status === "running" ? "bg-green-100 text-green-700" : vm.status === "occupied" ? "bg-blue-100 text-blue-700" : "bg-surface-200 text-surface-600"}`}>{vm.status}</span>
                  {vm.agent_id && <span className="text-[9px] text-surface-400">agent: {vm.agent_id.slice(0, 8)}</span>}
                  <div className="flex gap-1">
                    {vm.status === "running" && <button onClick={() => action(vm.id, "stop")} className="rounded bg-yellow-600 px-2 py-1 text-[9px] text-white hover:bg-yellow-700">Stop</button>}
                    {vm.status === "stopped" && <button onClick={() => action(vm.id, "start")} className="rounded bg-green-600 px-2 py-1 text-[9px] text-white hover:bg-green-700">Start</button>}
                    <button onClick={() => action(vm.id, "destroy")} className="rounded bg-red-600 px-2 py-1 text-[9px] text-white hover:bg-red-700">Destroy</button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}