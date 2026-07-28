"use client";

import { useState, useEffect } from "react";

interface TourStep {
  title: string;
  content: string;
  target: string;
  position: "top" | "bottom" | "left" | "right";
}

const STEPS: TourStep[] = [
  { title: "Welcome to SuperDev", content: "This is your AI-powered development platform. Let's get you started!", target: "#welcome", position: "bottom" },
  { title: "Dashboard", content: "View your projects, workflows, and agent activity at a glance.", target: "#dashboard-link", position: "right" },
  { title: "Agents", content: "Create and manage AI agents that help you code, review, and deploy.", target: "#agents-link", position: "right" },
  { title: "Workflows", content: "Build automated pipelines with our visual workflow editor.", target: "#workflows-link", position: "right" },
  { title: "Studio", content: "Debug agents visually with breakpoints and step-by-step execution.", target: "#studio-link", position: "left" },
  { title: "Marketplace", content: "Extend SuperDev with plugins, integrations, and templates.", target: "#marketplace-link", position: "left" },
];

export function Tour() {
  const [isOpen, setIsOpen] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    const completed = localStorage.getItem("superdev_tour_completed");
    if (!completed) setIsOpen(true);
  }, []);

  const next = () => {
    if (currentStep < STEPS.length - 1) setCurrentStep(currentStep + 1);
    else complete();
  };

  const prev = () => { if (currentStep > 0) setCurrentStep(currentStep - 1); };

  const complete = () => {
    setIsOpen(false);
    setDismissed(true);
    localStorage.setItem("superdev_tour_completed", "true");
  };

  const skip = () => complete();

  if (!isOpen || dismissed) return null;

  const step = STEPS[currentStep];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <div className="mx-4 max-w-md rounded-xl bg-white p-6 shadow-2xl dark:bg-surface-900">
        <div className="mb-4 flex items-center justify-between">
          <span className="text-xs font-medium text-primary-600">Tour ({currentStep + 1}/{STEPS.length})</span>
          <button onClick={skip} className="text-surface-400 hover:text-surface-600">&times;</button>
        </div>
        <h3 className="text-lg font-bold text-surface-900 dark:text-surface-50">{step.title}</h3>
        <p className="mt-2 text-sm text-surface-600 dark:text-surface-400">{step.content}</p>
        <div className="mt-6 flex items-center justify-between">
          <div className="flex gap-1">
            {STEPS.map((_, i) => (
              <div key={i} className={`h-1.5 w-1.5 rounded-full ${i === currentStep ? "bg-primary-600" : "bg-surface-300"}`} />
            ))}
          </div>
          <div className="flex gap-2">
            {currentStep > 0 && <button onClick={prev} className="rounded-lg bg-surface-200 px-3 py-1.5 text-sm text-surface-700 dark:bg-surface-700 dark:text-surface-300">Back</button>}
            <button onClick={next} className="rounded-lg bg-primary-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-primary-700">
              {currentStep === STEPS.length - 1 ? "Finish" : "Next"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}