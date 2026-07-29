"use client";

import { DashboardLayout } from "@/components/DashboardLayout";
import { MCPBrowser } from "@/components/mcp/MCPBrowser";

export default function MCPPage() {
  return (
    <DashboardLayout>
      <h1 className="mb-6 text-2xl font-bold text-surface-900 dark:text-surface-50">MCP</h1>
      <MCPBrowser />
    </DashboardLayout>
  );
}
