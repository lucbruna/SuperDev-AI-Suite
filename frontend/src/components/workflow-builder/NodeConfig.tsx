"use client";

import { useState, useEffect } from "react";
import type { Node } from "reactflow";

interface NodeConfigProps {
  node: Node | null;
  onUpdate: (nodeId: string, config: any) => void;
}

export function NodeConfig({ node, onUpdate }: NodeConfigProps) {
  const [config, setConfig] = useState<Record<string, string>>({});

  useEffect(() => {
    if (node) setConfig(node.data.config || {});
  }, [node]);

  if (!node) {
    return (
      <div className="w-64 rounded-xl border bg-white p-4 dark:border-surface-700 dark:bg-surface-900">
        <p className="text-sm text-surface-400">Select a node to configure</p>
      </div>
    );
  }

  const fields = getFieldsForLabel(node.data.label);

  const updateField = (key: string, value: string) => {
    const newConfig = { ...config, [key]: value };
    setConfig(newConfig);
    onUpdate(node.id, newConfig);
  };

  return (
    <div className="w-64 rounded-xl border bg-white p-4 dark:border-surface-700 dark:bg-surface-900">
      <h3 className="text-sm font-semibold text-surface-900 dark:text-surface-50">Configure</h3>
      <p className="text-xs text-surface-400">{node.data.label} ({node.id})</p>
      <div className="mt-3 space-y-3">
        {fields.map((f) => (
          <div key={f.key}>
            <label className="text-xs font-medium text-surface-600">{f.label}</label>
            {f.type === "select" ? (
              <select value={config[f.key] || f.default || ""} onChange={(e) => updateField(f.key, e.target.value)} className="mt-1 w-full rounded-lg border border-surface-300 bg-white px-2 py-1.5 text-xs dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100">
                {(f.options || []).map((o) => <option key={o} value={o}>{o}</option>)}
              </select>
            ) : (
              <input type={f.type || "text"} value={config[f.key] || f.default || ""} onChange={(e) => updateField(f.key, e.target.value)} placeholder={f.placeholder} className="mt-1 w-full rounded-lg border border-surface-300 bg-white px-2 py-1.5 text-xs dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function getFieldsForLabel(label: string) {
  const allFields: Record<string, { key: string; label: string; type: string; placeholder?: string; default?: string; options?: string[] }[]> = {
    "Agent Task": [
      { key: "agent", label: "Agent", type: "select", options: ["Architect", "Executor", "Reviewer", "Deployer"], default: "Executor" },
      { key: "prompt", label: "Instruction", type: "text", placeholder: "Describe the task..." },
      { key: "model", label: "Model", type: "select", options: ["gpt-4o", "claude-3", "gemini-1.5"], default: "gpt-4o" },
    ],
    "HTTP Request": [
      { key: "url", label: "URL", type: "text", placeholder: "https://api.example.com" },
      { key: "method", label: "Method", type: "select", options: ["GET", "POST", "PUT", "DELETE"], default: "GET" },
      { key: "headers", label: "Headers (JSON)", type: "text", placeholder: '{"Auth": "Bearer..."}' },
    ],
    "Condition": [
      { key: "field", label: "Variable", type: "text", placeholder: "result.status" },
      { key: "operator", label: "Operator", type: "select", options: ["==", "!=", ">", "<", "contains"], default: "==" },
      { key: "value", label: "Value", type: "text", placeholder: "success" },
    ],
    "Notification": [
      { key: "channel", label: "Channel", type: "select", options: ["slack", "email", "webhook"], default: "slack" },
      { key: "message", label: "Message", type: "text", placeholder: "Workflow completed!" },
    ],
    "Wait": [
      { key: "duration", label: "Duration (seconds)", type: "number", placeholder: "60", default: "60" },
    ],
    "Loop": [
      { key: "max_iterations", label: "Max Iterations", type: "number", placeholder: "10", default: "10" },
      { key: "collection", label: "Collection Variable", type: "text", placeholder: "items" },
    ],
  };
  return allFields[label] || [{ key: "value", label: "Value", type: "text", placeholder: "Configure..." }];
}