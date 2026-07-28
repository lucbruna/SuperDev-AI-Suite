"use client";

const NODE_TYPES = [
  { type: "Start", icon: "▶️", category: "control" },
  { type: "End", icon: "⏹️", category: "control" },
  { type: "Agent Task", icon: "🤖", category: "agents" },
  { type: "Code Execute", icon: "💻", category: "execution" },
  { type: "HTTP Request", icon: "🌐", category: "integration" },
  { type: "Condition", icon: "🔀", category: "control" },
  { type: "Loop", icon: "🔄", category: "control" },
  { type: "Wait", icon: "⏳", category: "control" },
  { type: "Notification", icon: "🔔", category: "integration" },
  { type: "Approval", icon: "✅", category: "human" },
  { type: "AI Review", icon: "🔍", category: "agents" },
  { type: "Deploy", icon: "🚀", category: "devops" },
];

export function NodePalette() {
  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData("application/reactflow", nodeType);
    event.dataTransfer.effectAllowed = "move";
  };

  const categories = [...new Set(NODE_TYPES.map((n) => n.category))];

  return (
    <div className="w-48 rounded-xl border bg-white p-3 dark:border-surface-700 dark:bg-surface-900">
      <h3 className="mb-3 text-xs font-semibold text-surface-500 uppercase">Nodes</h3>
      {categories.map((cat) => (
        <div key={cat} className="mb-3">
          <p className="mb-1 text-xs text-surface-400 capitalize">{cat}</p>
          {NODE_TYPES.filter((n) => n.category === cat).map((n) => (
            <div
              key={n.type}
              draggable
              onDragStart={(e) => onDragStart(e, n.type)}
              className="mb-1 flex cursor-grab items-center gap-2 rounded-lg bg-surface-50 px-2 py-1.5 text-xs text-surface-700 hover:bg-primary-50 hover:text-primary-700 active:cursor-grabbing dark:bg-surface-800 dark:text-surface-300"
            >
              <span>{n.icon}</span>
              <span>{n.type}</span>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}