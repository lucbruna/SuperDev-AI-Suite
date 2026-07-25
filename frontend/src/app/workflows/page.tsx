"use client";

import dynamic from "next/dynamic";

const WorkflowCanvas = dynamic(
  () => import("@/workflow/WorkflowCanvas").then((m) => ({ default: m.WorkflowCanvas })),
  { ssr: false, loading: () => <div className="p-8 text-center">Loading workflows...</div> }
);

export default function WorkflowsPage() {
  return (
    <div className="container mx-auto p-6">
      <WorkflowCanvas />
    </div>
  );
}