"use client";

import { Modal } from "@/components/modals/Modal";
import { OrganizationForm } from "@/components/forms/OrganizationForm";

interface CreateOrganizationDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { name: string; slug: string; description: string; website: string; logo_url: string }) => void;
  isLoading?: boolean;
}

export function CreateOrganizationDialog({
  isOpen,
  onClose,
  onSubmit,
  isLoading,
}: CreateOrganizationDialogProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create Organization" size="lg">
      <OrganizationForm
        onSubmit={onSubmit}
        onCancel={onClose}
        isLoading={isLoading}
      />
    </Modal>
  );
}
