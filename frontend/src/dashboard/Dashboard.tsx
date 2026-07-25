"use client";

import React from "react";
import { StatCard } from "@/components/cards/StatCard";
import { Card, CardHeader, CardBody } from "@/components/cards/Card";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";

const stats = [
  { label: "Total Projects", value: "12", change: "+2 this week", trend: { value: "+2 this week", direction: "up" as const } },
  { label: "Active Agents", value: "5", change: "3 running", trend: { value: "3 running", direction: "up" as const } },
  { label: "API Calls", value: "1,234", change: "+12% vs last month", trend: { value: "+12% vs last month", direction: "up" as const } },
  { label: "Tokens Used", value: "45.2K", change: "$0.85 cost", trend: { value: "$0.85 cost", direction: "down" as const } },
];

const recentActivity = [
  { id: "1", type: "agent", message: "Code Assistant completed review", time: "2 min ago", status: "success" },
  { id: "2", type: "workflow", message: "Deploy pipeline finished", time: "15 min ago", status: "success" },
  { id: "3", type: "agent", message: "Debugger started analysis", time: "30 min ago", status: "running" },
  { id: "4", type: "project", message: "New project created: superdev-api", time: "1 hour ago", status: "info" },
  { id: "5", type: "error", message: "Runtime timeout in test suite", time: "2 hours ago", status: "error" },
];

const quickActions = [
  { label: "New Project", icon: "+", href: "/projects/new" },
  { label: "Run Agent", icon: "AI", href: "/agents" },
  { label: "Execute Code", icon: ">", href: "/runtime" },
  { label: "View Workflows", icon: "~", href: "/workflows" },
];

export function Dashboard() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <Button variant="primary" size="sm">New Project</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <StatCard
            key={stat.label}
            icon={null}
            label={stat.label}
            value={stat.value}
            trend={stat.trend}
          />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <h2 className="text-lg font-semibold">Recent Activity</h2>
          </CardHeader>
          <CardBody>
            <div className="space-y-3">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                  <div className="flex items-center gap-3">
                    <Badge variant={activity.status === "success" ? "success" : activity.status === "error" ? "danger" : activity.status === "running" ? "warning" : "default"}>
                      {activity.type}
                    </Badge>
                    <span className="text-sm">{activity.message}</span>
                  </div>
                  <span className="text-xs text-muted-foreground">{activity.time}</span>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold">Quick Actions</h2>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-2 gap-3">
              {quickActions.map((action) => (
                <a
                  key={action.label}
                  href={action.href}
                  className="flex flex-col items-center gap-2 p-4 rounded-lg border border-border/50 hover:bg-accent/50 transition-colors"
                >
                  <span className="text-2xl font-mono">{action.icon}</span>
                  <span className="text-sm font-medium">{action.label}</span>
                </a>
              ))}
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
