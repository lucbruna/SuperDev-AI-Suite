"use client";

import { useState } from "react";
import { Card, CardHeader, CardBody, CardFooter } from "@/components/cards/Card";
import { Button } from "@/components/buttons/Button";

const steps = [
  { title: "Welcome", description: "Create your first project" },
  { title: "Connect", description: "Link your AI providers" },
  { title: "Configure", description: "Set up your workspace" },
  { title: "Launch", description: "Deploy your first agent" },
];

export function OnboardingWizard() {
  const [step, setStep] = useState(0);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <h2 className="text-xl font-bold">{steps[step].title}</h2>
          <p className="text-sm text-muted-foreground">{steps[step].description}</p>
        </CardHeader>
        <CardBody>
          <div className="flex gap-2 mb-6">
            {steps.map((s, i) => (
              <div
                key={i}
                className={`h-2 flex-1 rounded-full ${i <= step ? "bg-primary" : "bg-muted"}`}
              />
            ))}
          </div>
          <p className="text-center py-8 text-muted-foreground">
            Step {step + 1} of {steps.length}
          </p>
        </CardBody>
        <CardFooter>
          {step > 0 && (
            <Button variant="ghost" onClick={() => setStep(step - 1)}>
              Back
            </Button>
          )}
          {step < steps.length - 1 ? (
            <Button variant="primary" onClick={() => setStep(step + 1)}>
              Next
            </Button>
          ) : (
            <Button variant="primary" onClick={() => {}}>
              Get Started
            </Button>
          )}
        </CardFooter>
      </Card>
    </div>
  );
}