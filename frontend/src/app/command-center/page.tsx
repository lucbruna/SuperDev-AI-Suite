import { KanbanBoard } from "../../components/command-center/KanbanBoard";

export default function CommandCenterPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-bold text-surface-900 dark:text-surface-50">Agent Command Center</h1>
        <p className="text-sm text-surface-500">Visual Kanban dashboard showing all agents, their status, and real-time progress</p>
      </div>
      <KanbanBoard />
    </div>
  );
}