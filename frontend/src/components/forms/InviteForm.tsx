"use client";

import { useState, type FormEvent } from "react";
import { Input } from "@/components/inputs/Input";
import { Select } from "@/components/inputs/Select";
import { FormField } from "@/components/forms/FormField";
import { Button } from "@/components/buttons/Button";
import { validators } from "@/utils/validation";

const ROLE_OPTIONS = [
  { value: "member", label: "Member" },
  { value: "admin", label: "Admin" },
];

interface InviteFormData {
  email: string;
  role: string;
  message: string;
}

interface InviteFormProps {
  onSubmit: (data: InviteFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function InviteForm({ onSubmit, onCancel, isLoading }: InviteFormProps) {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("member");
  const [message, setMessage] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    const emailErr = validators.email(email);
    if (emailErr) errs.email = emailErr;
    if (!email.trim()) errs.email = "Email is required";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    onSubmit({ email: email.trim(), role, message: message.trim() });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <Input
        label="Email Address"
        type="email"
        placeholder="colleague@example.com"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        error={errors.email}
        autoFocus
      />

      <Select
        label="Role"
        options={ROLE_OPTIONS}
        value={role}
        onChange={(e) => setRole(e.target.value)}
      />

      <FormField label="Message (optional)">
        <textarea
          className="flex min-h-[80px] w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-sm text-surface-900 placeholder:text-surface-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-0 dark:bg-surface-900 dark:text-surface-100 dark:border-surface-600 dark:focus:ring-primary-400"
          placeholder="Add a personal message to the invitation..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
      </FormField>

      <div className="flex justify-end gap-3 pt-2">
        <Button type="button" variant="secondary" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" isLoading={isLoading}>
          Send Invitation
        </Button>
      </div>
    </form>
  );
}
