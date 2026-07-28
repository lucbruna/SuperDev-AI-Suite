"use client";

import { useState, useCallback, useRef } from "react";
import ReactFlow, {
  addEdge, Background, Controls, MiniMap, useNodesState, useEdgesState,
  Node, Edge, Connection, NodeTypes, ReactFlowProvider,
} from "reactflow";
import "reactflow/dist/style.css";
import { NodePalette } from "./NodePalette";
import { NodeConfig } from "./NodeConfig";

const initialNodes: Node[] = [
  { id: "start", type: "input", position: { x: 250, y: 0 }, data: { label: "Start", config: {} } },
  { id: "end", type: "output", position: { x: 250, y: 400 }, data: { label: "End", config: {} } },
];

const initialEdges: Edge[] = [];

function CustomNode({ data }: { data: { label: string; icon?: string } }) {
  return (
    <div className="rounded-xl border-2 border-primary-200 bg-white px-4 py-2 shadow-sm dark:border-primary-800 dark:bg-surface-800">
      <div className="flex items-center gap-2">
        <span className="text-lg">{data.icon || "⚡"}</span>
        <span className="text-sm font-medium text-surface-900 dark:text-surface-50">{data.label}</span>
      </div>
    </div>
  );
}

const nodeTypes: NodeTypes = { custom: CustomNode };

function FlowCanvas() {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null);

  const onConnect = useCallback((params: Connection) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    const type = event.dataTransfer.getData("application/reactflow");
    if (!type || !reactFlowInstance) return;
    const position = reactFlowInstance.screenToFlowPosition({ x: event.clientX, y: event.clientY });
    const newId = `node_${Date.now()}`;
    const newNode: Node = {
      id: newId, type: "custom", position,
      data: { label: type, icon: "⚙️", config: {} },
    };
    setNodes((nds) => [...nds, newNode]);
  }, [reactFlowInstance, setNodes]);

  const onNodeClick = useCallback((_: any, node: Node) => setSelectedNode(node), []);

  const onConfigUpdate = useCallback((nodeId: string, config: any) => {
    setNodes((nds) => nds.map((n) => (n.id === nodeId ? { ...n, data: { ...n.data, config } } : n)));
  }, [setNodes]);

  const exportWorkflow = () => {
    const wf = { nodes: nodes.map((n) => ({ id: n.id, type: n.type || "custom", label: n.data.label, config: n.data.config, position: n.position })), edges: edges.map((e) => ({ id: e.id, source: e.source, target: e.target })) };
    navigator.clipboard.writeText(JSON.stringify(wf, null, 2));
  };

  return (
    <div className="flex h-[600px] gap-4">
      <NodePalette />
      <div ref={reactFlowWrapper} className="flex-1 rounded-xl border bg-white dark:border-surface-700 dark:bg-surface-900">
        <ReactFlow
          nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange}
          onConnect={onConnect} onInit={setReactFlowInstance} onDrop={onDrop} onDragOver={onDragOver}
          onNodeClick={onNodeClick} nodeTypes={nodeTypes} fitView
        >
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
      <NodeConfig node={selectedNode} onUpdate={onConfigUpdate} />
      <div className="absolute bottom-24 right-8 flex gap-2">
        <button onClick={exportWorkflow} className="rounded-lg bg-primary-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-primary-700">Export JSON</button>
      </div>
    </div>
  );
}

export function WorkflowBuilder() {
  return (
    <ReactFlowProvider>
      <FlowCanvas />
    </ReactFlowProvider>
  );
}