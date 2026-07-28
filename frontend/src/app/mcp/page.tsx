"use client";

import { MCPBrowser } from "@/components/mcp/MCPBrowser";
import { MCPConsole } from "@/components/mcp/MCPConsole";
import { MCPProviderConfig } from "@/components/mcp/MCPProviderConfig";

export default function MCPPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-bold text-surface-900 dark:text-surface-50">MCP Protocol</h1>
        <p className="text-sm text-surface-500">
          Model Context Protocol — connect any tool, data source, or service to your AI agents
        </p>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2">
          <MCPBrowser />
        </div>
        <div>
          <MCPConsole />
        </div>
      </div>
      <MCPProviderConfig />
    </div>
  );
}