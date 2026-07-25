"use client";

import type { ReactNode } from "react";
import { Modal } from "@/components/modals/Modal";
import { Button } from "@/components/buttons/Button";

interface AlertDialogProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  message: string | ReactNode;
  variant?: "info" | "warning" | "error";
  confirmLabel?: string;
  cancelLabel?: string;
  showCancel?: boolean;
  onConfirm?: () => void;
  onCancel?: () => void;
}

const variantStyles = {
  info: {
    icon: (
      <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    buttonVariant: "primary" as const,
    bgClass: "bg-blue-50 dark:bg-blue-900/20",
  },
  warning: {
    icon: (
      <svg className="h-6 w-6 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
      </svg>
    ),
    buttonVariant: "secondary" as const,
    bgClass: "bg-amber-50 dark:bg-amber-900/20",
  },
  error: {
    icon: (
      <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    buttonVariant: "danger" as const,
    bgClass: "bg-red-50 dark:bg-red-900/20",
  },
};

export function AlertDialog({
  isOpen,
  onClose,
  title,
  message,
  variant = "info",
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  showCancel = false,
  onConfirm,
  onCancel,
}: AlertDialogProps) {
  const styles = variantStyles[variant];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm" showCloseButton={false}>
      <div className="space-y-6">
        <div className="flex items-start gap-4">
          <div className={`flex-shrink-0 rounded-full p-2 ${styles.bgClass}`}>
            {styles.icon}
          </div>
          <div className="min-w-0 flex-1 pt-0.5 text-sm text-surface-600 dark:text-surface-400">
            {typeof message === "string" ? <p>{message}</p> : message}
          </div>
        </div>
        <div className="flex justify-end gap-3">
          {showCancel && (
            <Button variant="secondary" onClick={onCancel ?? onClose}>
              {cancelLabel}
            </Button>
          )}
          <Button variant={styles.buttonVariant} onClick={onConfirm ?? onClose}>
            {confirmLabel}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
