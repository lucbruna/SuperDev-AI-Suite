"use client";

import { useState } from "react";

export function IssueToPR() {
  const [repo, setRepo] = useState("");
  const [issueNumber, setIssueNumber] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const generate = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch("/api/issue-to-pr/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo: repo || "owner/repo", issue_number: parseInt(issueNumber) || 1 }),
      });
      setResult(await res.json());
    } catch (err: any) {
      setResult({ error: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-xl border dark:border-surface-700">
      <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
        <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Issue → PR Generator</span>
      </div>
      <div className="space-y-3 p-4">
        <input value={repo} onChange={(e) => setRepo(e.target.value)} placeholder="Repository (e.g., owner/repo)" className="w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100" />
        <input value={issueNumber} onChange={(e) => setIssueNumber(e.target.value)} placeholder="Issue number" type="number" className="w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100" />
        <button onClick={generate} disabled={loading} className="w-full rounded-lg bg-primary-600 py-2 text-xs font-medium text-white hover:bg-primary-700 disabled:opacity-40">
          {loading ? "Generating..." : "Generate PR"}
        </button>
        {result && (
          <pre className="overflow-x-auto rounded-lg bg-surface-100 p-3 text-[10px] dark:bg-surface-800 dark:text-surface-300">
            {JSON.stringify(result, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}