"use client";

import { Card, CardHeader, CardBody, CardFooter } from "@/components/cards/Card";
import { Button } from "@/components/buttons/Button";

export default function SettingsPage() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>
      <Card>
        <CardHeader><h2 className="text-lg font-semibold">General</h2></CardHeader>
        <CardBody>
          <p className="text-sm text-muted-foreground">Configure your application preferences here.</p>
        </CardBody>
      </Card>
      <Card>
        <CardHeader><h2 className="text-lg font-semibold">API Keys</h2></CardHeader>
        <CardBody>
          <p className="text-sm text-muted-foreground mb-4">Manage your API keys for external integrations.</p>
          <Button variant="primary" size="sm">Generate New Key</Button>
        </CardBody>
      </Card>
    </div>
  );
}