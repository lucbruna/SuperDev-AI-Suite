"use client";

import dynamic from "next/dynamic";
import { Card, CardHeader, CardBody } from "@/components/cards/Card";

const Terminal = dynamic(
  () => import("@/terminal/Terminal").then((m) => ({ default: m.Terminal })),
  { ssr: false, loading: () => <div className="p-8 text-center">Loading terminal...</div> }
);

export default function RuntimePage() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold">Runtime Environment</h1>
      <Card>
        <CardHeader>
          <h2 className="text-lg font-semibold">Code Execution Terminal</h2>
        </CardHeader>
        <CardBody>
          <div className="h-[500px] rounded-lg overflow-hidden border border-border">
            <Terminal />
          </div>
        </CardBody>
      </Card>
    </div>
  );
}