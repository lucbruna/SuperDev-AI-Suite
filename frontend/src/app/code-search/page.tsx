import { CodeSearchPanel } from "../../components/code-search/CodeSearchPanel";

export default function CodeSearchPage() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-lg font-bold text-surface-900 dark:text-surface-50">Code Search</h1>
        <p className="text-sm text-surface-500">Semantic search across your entire codebase — powered by full-text indexing with file preview</p>
      </div>
      <CodeSearchPanel />
    </div>
  );
}