"use client";

import { Modal } from "@/components/modals/Modal";
import { ProjectForm } from "@/components/forms/ProjectForm";

interface CreateProjectDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { name: string; description: string; template: string; language: string; tags: string[] }) => void;
  isLoading?: boolean;
}

export function CreateProjectDialog({
  isOpen,
  onClose,
  onSubmit,
  isLoading,
}: CreateProjectDialogProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create Project" size="lg">
      <ProjectForm
        onSubmit={onSubmit}
        onCancel={onClose}
        isLoading={isLoading}
      />
    </Modal>
  );
}
