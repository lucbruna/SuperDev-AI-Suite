"use client";

import { Card, CardHeader, CardBody } from "@/components/cards/Card";

interface CostData {
  total: number;
  byProvider: Record<string, number>;
  byProject: Record<string, number>;
}

export function CostDashboard() {
  const costData: CostData = {
    total: 1234.56,
    byProvider: { openai: 800, anthropic: 300, gemini: 134.56 },
    byProject: { "superdev-api": 500, "agent-core": 400, "workflow-engine": 334.56 },
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Cost Management</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardBody>
            <p className="text-sm text-muted-foreground">Total Spend</p>
            <p className="text-3xl font-bold">${costData.total.toFixed(2)}</p>
          </CardBody>
        </Card>
      </div>
      <Card>
        <CardHeader><h3 className="font-semibold">By Provider</h3></CardHeader>
        <CardBody>
          {Object.entries(costData.byProvider).map(([provider, amount]) => (
            <div key={provider} className="flex justify-between py-2 border-b last:border-0">
              <span className="capitalize">{provider}</span>
              <span className="font-mono">${amount.toFixed(2)}</span>
            </div>
          ))}
        </CardBody>
      </Card>
      <Card>
        <CardHeader><h3 className="font-semibold">By Project</h3></CardHeader>
        <CardBody>
          {Object.entries(costData.byProject).map(([project, amount]) => (
            <div key={project} className="flex justify-between py-2 border-b last:border-0">
              <span>{project}</span>
              <span className="font-mono">${amount.toFixed(2)}</span>
            </div>
          ))}
        </CardBody>
      </Card>
    </div>
  );
}