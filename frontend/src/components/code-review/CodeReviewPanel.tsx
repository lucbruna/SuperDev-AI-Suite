"use client";

import { useState } from "react";
import { api } from "@/utils/api-fetch";

interface ReviewResult {
  conclusion: string;
  score: number;
  summary: string;
  comments: Array<{ path: string; body: string; line: number }>;
  total_issues: number;
}

export function CodeReviewPanel() {
  const [repo, setRepo] = useState("");
  const [prNumber, setPrNumber] = useState("");
  const [result, setResult] = useState<ReviewResult | null>(null);
  const [loading, setLoading] = useState(false);

  const runReview = async () => {
    setLoading(true);
    setResult(null);
    try {
      const data = await api.post<any>("/code-review/run", {
        repo: repo || "owner/repo",
        pr_number: parseInt(prNumber) || 1,
        sha: "mock_sha",
      });
      setResult(data);
    } catch (err: any) {
      setResult({ conclusion: "error", score: 0, summary: err.message, comments: [], total_issues: 0 });
    } finally {
      setLoading(false);
    }
  };

  const conclusionColor = (c: string) =>
    c === "success" ? "text-green-400 bg-green-950/30" : c === "failure" ? "text-red-400 bg-red-950/30" : "text-yellow-400 bg-yellow-950/30";

  return (
    <div className="rounded-xl border dark:border-surface-700">
      <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
        <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">AI Code Review</span>
      </div>
      <div className="space-y-3 p-4">
        <input value={repo} onChange={(e) => setRepo(e.target.value)} placeholder="Repository" className="w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100" />
        <input value={prNumber} onChange={(e) => setPrNumber(e.target.value)} placeholder="PR number" type="number" className="w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100" />
        <button onClick={runReview} disabled={loading} className="w-full rounded-lg bg-primary-600 py-2 text-xs font-medium text-white hover:bg-primary-700 disabled:opacity-40">
          {loading ? "Reviewing..." : "Run Review"}
        </button>
        {result && (
          <div className={`rounded-lg p-3 ${conclusionColor(result.conclusion)}`}>
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase">{result.conclusion} — Score {result.score}/10</span>
              <span className="text-[10px] opacity-70">{result.total_issues} issues</span>
            </div>
            <p className="mt-2 text-xs opacity-80">{result.summary.slice(0, 200)}</p>
            {result.comments.length > 0 && (
              <details className="mt-2">
                <summary className="cursor-pointer text-[10px] opacity-70 hover:opacity-100">{result.comments.length} inline comments</summary>
                <div className="mt-1 space-y-1">
                  {result.comments.map((c, i) => (
                    <div key={i} className="rounded bg-black/20 px-2 py-1">
                      <span className="text-[10px] font-mono opacity-60">{c.path}:{c.line}</span>
                      <p className="text-[10px]">{c.body.slice(0, 150)}</p>
                    </div>
                  ))}
                </div>
              </details>
            )}
          </div>
        )}
      </div>
    </div>
  );
}