"use client";

import { useState } from "react";

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

const MOCK_PLUGINS: Plugin[] = [
  { id: "text-formatter", name: "Text Formatter", version: "1.2.0", author: "SuperDev Team", description: "Format and beautify text content with customizable rules", category: "tool", downloads: 1520, rating: 4.5, tags: ["text", "format"] },
  { id: "ai-assistant", name: "AI Assistant Provider", version: "2.0.1", author: "SuperDev Team", description: "AI-powered code assistance provider with multi-model support", category: "provider", downloads: 3400, rating: 4.8, tags: ["ai", "provider"] },
  { id: "code-analyzer", name: "Code Analyzer Agent", version: "1.0.0", author: "Community", description: "Static code analysis agent for security and quality", category: "agent", downloads: 890, rating: 4.2, tags: ["code", "analysis"] },
  { id: "slack-notifier", name: "Slack Notifier", version: "1.1.0", author: "SuperDev Team", description: "Send notifications to Slack channels from workflows", category: "integration", downloads: 2100, rating: 4.6, tags: ["slack", "notification"] },
  { id: "github-sync", name: "GitHub Sync", version: "1.0.0", author: "Community", description: "Sync workflows with GitHub repositories and PRs", category: "integration", downloads: 1560, rating: 4.4, tags: ["github", "sync"] },
  { id: "docker-deploy", name: "Docker Deploy", version: "0.9.0", author: "Community", description: "Deploy agents and workflows in Docker containers", category: "runtime", downloads: 780, rating: 3.9, tags: ["docker", "deploy"] },
  { id: "mcp-server", name: "MCP Server", version: "0.1.0", author: "SuperDev Team", description: "Model Context Protocol server for tool integration", category: "protocol", downloads: 450, rating: 4.0, tags: ["mcp", "protocol"] },
  { id: "web-scraper", name: "Web Scraper Tool", version: "1.0.0", author: "Community", description: "Extract and parse web content for agent consumption", category: "tool", downloads: 320, rating: 3.7, tags: ["web", "scraping"] },
];

const CATEGORIES = ["all", "tool", "provider", "agent", "integration", "runtime", "protocol"];

export default function MarketplacePage() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");
  const [sort, setSort] = useState<"downloads" | "rating" | "name">("downloads");
  const [installing, setInstalling] = useState<string | null>(null);

  const filtered = MOCK_PLUGINS
    .filter((p) => category === "all" || p.category === category)
    .filter((p) => !search || p.name.toLowerCase().includes(search.toLowerCase()) || p.description.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => sort === "downloads" ? b.downloads - a.downloads : sort === "rating" ? b.rating - a.rating : a.name.localeCompare(b.name));

  const handleInstall = (id: string) => {
    setInstalling(id);
    setTimeout(() => setInstalling(null), 1500);
  };

  const stars = (rating: number) => {
    const full = Math.floor(rating);
    const half = rating % 1 >= 0.5;
    return "★".repeat(full) + (half ? "½" : "") + "☆".repeat(5 - full - (half ? 1 : 0));
  };

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950">
      <header className="border-b bg-white dark:border-surface-700 dark:bg-surface-900">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <h1 className="text-xl font-bold text-primary-600">SuperDev</h1>
          <nav className="flex items-center gap-4">
            <a href="/dashboard" className="text-sm font-medium text-surface-600 hover:text-surface-900 dark:text-surface-400">Dashboard</a>
            <a href="/marketplace" className="text-sm font-medium text-primary-600">Marketplace</a>
            <a href="/studio" className="text-sm font-medium text-surface-600 hover:text-surface-900 dark:text-surface-400">Studio</a>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Plugin Marketplace</h2>
            <p className="mt-1 text-sm text-surface-600 dark:text-surface-400">Discover and install plugins, integrations, and agents</p>
          </div>
          <div className="flex items-center gap-2 text-sm text-surface-500">
            <span>{MOCK_PLUGINS.length} plugins</span>
            <span>|</span>
            <span>{MOCK_PLUGINS.reduce((s, p) => s + p.downloads, 0).toLocaleString()} downloads</span>
          </div>
        </div>

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search plugins..."
            className="flex-1 min-w-[200px] rounded-lg border border-surface-300 bg-white px-4 py-2 text-sm focus:border-primary-500 focus:outline-none dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100"
          />
          <div className="flex gap-1">
            {CATEGORIES.map((cat) => (
              <button key={cat} onClick={() => setCategory(cat)} className={`rounded-lg px-3 py-1.5 text-xs font-medium ${category === cat ? "bg-primary-600 text-white" : "bg-surface-200 text-surface-600 dark:bg-surface-700 dark:text-surface-400 hover:bg-surface-300"}`}>
                {cat === "all" ? "All" : cat.charAt(0).toUpperCase() + cat.slice(1)}
              </button>
            ))}
          </div>
          <select value={sort} onChange={(e) => setSort(e.target.value as any)} className="rounded-lg border border-surface-300 bg-white px-3 py-2 text-sm dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100">
            <option value="downloads">Most Downloaded</option>
            <option value="rating">Highest Rated</option>
            <option value="name">Name A-Z</option>
          </select>
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map((plugin) => (
            <div key={plugin.id} className="flex flex-col rounded-xl border bg-white p-5 shadow-sm transition-shadow hover:shadow-md dark:border-surface-700 dark:bg-surface-900">
              <div className="flex items-start justify-between">
                <span className="rounded bg-primary-100 px-2 py-0.5 text-xs font-medium text-primary-700 dark:bg-primary-900 dark:text-primary-300">{plugin.category}</span>
                <span className="text-xs text-surface-400">v{plugin.version}</span>
              </div>
              <h3 className="mt-3 font-semibold text-surface-900 dark:text-surface-50">{plugin.name}</h3>
              <p className="mt-1 text-xs text-surface-500">by {plugin.author}</p>
              <p className="mt-2 flex-1 text-sm text-surface-600 dark:text-surface-400">{plugin.description}</p>
              <div className="mt-3 flex items-center justify-between">
                <div className="flex items-center gap-1">
                  <span className="text-xs text-yellow-500">{stars(plugin.rating)}</span>
                  <span className="text-xs text-surface-400">{plugin.rating.toFixed(1)}</span>
                </div>
                <span className="text-xs text-surface-400">{plugin.downloads.toLocaleString()} downloads</span>
              </div>
              <div className="mt-2 flex flex-wrap gap-1">
                {plugin.tags.map((tag) => (
                  <span key={tag} className="rounded bg-surface-100 px-1.5 py-0.5 text-xs text-surface-500 dark:bg-surface-700">{tag}</span>
                ))}
              </div>
              <button
                onClick={() => handleInstall(plugin.id)}
                disabled={installing === plugin.id}
                className={`mt-4 w-full rounded-lg py-2 text-sm font-medium transition-colors ${installing === plugin.id ? "bg-green-500 text-white" : "bg-primary-600 text-white hover:bg-primary-700"}`}
              >
                {installing === plugin.id ? "Installed!" : "Install"}
              </button>
            </div>
          ))}
        </div>

        {filtered.length === 0 && (
          <div className="mt-12 text-center text-surface-500">
            <p className="text-lg">No plugins found</p>
            <p className="text-sm">Try a different search term or category</p>
          </div>
        )}
      </main>
    </div>
  );
}