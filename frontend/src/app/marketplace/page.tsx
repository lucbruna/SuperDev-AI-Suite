"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/DashboardLayout";

interface Plugin {
  id: string;
  name: string;
  version: string;
  author: string;
  description: string;
  category: string;
  downloads: number;
  rating: number;
  tags: string[];
}

export default function MarketplacePage() {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");
  const [installing, setInstalling] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/v1/plugins/registry")
      .then((r) => r.json())
      .then((d) => setPlugins(Array.isArray(d) ? d : d.data || []))
      .catch(() => setPlugins([]));
  }, []);

  const categories = ["all", ...new Set(plugins.map((p) => p.category))];

  const filtered = plugins
    .filter((p) => category === "all" || p.category === category)
    .filter((p) => !search || p.name.toLowerCase().includes(search.toLowerCase()) || p.description.toLowerCase().includes(search.toLowerCase()));

  const handleInstall = async (id: string) => {
    setInstalling(id);
    try {
      await fetch("/api/v1/plugins/install", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ slug: id }) });
    } catch {}
    setTimeout(() => setInstalling(null), 1500);
  };

  const stars = (rating: number) => {
    const full = Math.floor(rating);
    const half = rating % 1 >= 0.5;
    return "★".repeat(full) + (half ? "½" : "") + "☆".repeat(5 - full - (half ? 1 : 0));
  };

  return (
    <DashboardLayout>
      <h1 className="mb-1 text-2xl font-bold text-surface-900 dark:text-surface-50">Plugin Marketplace</h1>
      <p className="mb-6 text-sm text-surface-500">Descubra e instale plugins e integrações</p>

      <div className="mb-6 flex flex-wrap items-center gap-3">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar plugins..."
          className="flex-1 min-w-[200px] rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
        />
        <div className="flex flex-wrap gap-1">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategory(cat)}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium ${
                category === cat
                  ? "bg-primary-600 text-white"
                  : "bg-surface-200 text-surface-600 dark:bg-surface-700"
              }`}
            >
              {cat === "all" ? "Todos" : cat.charAt(0).toUpperCase() + cat.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {filtered.map((plugin) => (
          <div key={plugin.id} className="flex flex-col rounded-xl border bg-white p-5 shadow-sm dark:border-surface-700 dark:bg-surface-900">
            <div className="flex items-start justify-between">
              <span className="rounded bg-primary-100 px-2 py-0.5 text-xs font-medium text-primary-700">
                {plugin.category}
              </span>
              <span className="text-xs text-surface-400">v{plugin.version}</span>
            </div>
            <h3 className="mt-3 font-semibold text-surface-900 dark:text-surface-50">{plugin.name}</h3>
            <p className="mt-1 text-xs text-surface-500">por {plugin.author}</p>
            <p className="mt-2 flex-1 text-sm text-surface-600">{plugin.description}</p>
            <div className="mt-3 flex items-center justify-between text-xs">
              <span className="text-yellow-500">{stars(plugin.rating)} {plugin.rating.toFixed(1)}</span>
              <span className="text-surface-400">{plugin.downloads?.toLocaleString()} downloads</span>
            </div>
            <button
              onClick={() => handleInstall(plugin.id)}
              disabled={installing === plugin.id}
              className={`mt-4 w-full rounded-lg py-2 text-sm font-medium transition-colors ${
                installing === plugin.id
                  ? "bg-green-500 text-white"
                  : "bg-primary-600 text-white hover:bg-primary-700"
              }`}
            >
              {installing === plugin.id ? "Instalado!" : "Instalar"}
            </button>
          </div>
        ))}
        {filtered.length === 0 && (
          <p className="col-span-full mt-8 text-center text-surface-400">Nenhum plugin encontrado</p>
        )}
      </div>
    </DashboardLayout>
  );
}
