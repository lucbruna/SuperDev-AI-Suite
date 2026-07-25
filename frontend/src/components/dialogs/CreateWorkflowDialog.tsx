"use client";

import { useState } from "react";
import { Modal } from "@/components/modals/Modal";
import { Input } from "@/components/inputs/Input";
import { Select } from "@/components/inputs/Select";
import { Button } from "@/components/buttons/Button";

const WORKFLOW_TEMPLATES = [
  { value: "blank", label: "Blank" },
  { value: "code-review", label: "Code Review" },
  { value: "ci-cd", label: "CI/CD" },
  { value: "documentation", label: "Documentation" },
];

interface CreateWorkflowDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { name: string; description: string; template: string }) => void;
  isLoading?: boolean;
}

export function CreateWorkflowDialog({
  isOpen,
  onClose,
  onSubmit,
  isLoading,
}: CreateWorkflowDialogProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [template, setTemplate] = useState("blank");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ name, description, template });
    setName("");
    setDescription("");
    setTemplate("blank");
  };

  const handleClose = () => {
    setName("");
    setDescription("");
    setTemplate("blank");
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Create Workflow" size="lg">
      <form onSubmit={handleSubmit} className="space-y-5">
        <Input
          label="Name"
          placeholder="Enter workflow name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <Input
          label="Description"
          placeholder="Enter workflow description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <Select
          label="Template"
          options={WORKFLOW_TEMPLATES}
          value={template}
          onChange={(e) => setTemplate(e.target.value)}
        />
        <div className="flex justify-end gap-3 pt-2">
          <Button type="button" variant="secondary" onClick={handleClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" isLoading={isLoading}>
            Create
          </Button>
        </div>
      </form>
    </Modal>
  );
}
