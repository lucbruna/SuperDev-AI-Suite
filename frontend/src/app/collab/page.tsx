"use client";

import { CollaborativeEditor } from "../../components/editor/CollaborativeEditor";

export default function CollabPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-bold text-surface-900 dark:text-surface-50">Collaborative Editing</h1>
        <p className="text-sm text-surface-500">Real-time multi-user document editing with OT (Operational Transformation)</p>
      </div>
      <CollaborativeEditor />
    </div>
  );
}