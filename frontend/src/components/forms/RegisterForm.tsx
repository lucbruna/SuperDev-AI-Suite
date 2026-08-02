"use client";

import { useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Input } from "@/components/inputs/Input";
import { Button } from "@/components/buttons/Button";
import { useAuth } from "@/hooks/useAuth";
import { ROUTES } from "@/constants/routes";
import { validators } from "@/utils/validation";

export function RegisterForm() {
  const router = useRouter();
  const { register, isLoading, error, clearError } = useAuth();

  const [formData, setFormData] = useState({
    email: "",
    username: "",
    fullName: "",
    password: "",
    confirmPassword: "",
  });
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const updateField = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setFieldErrors((prev) => {
      const next = { ...prev };
      delete next[field];
      return next;
    });
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    const emailErr = validators.email(formData.email);
    if (emailErr) errors.email = emailErr;

    const usernameErr = validators.required(formData.username) ?? validators.username(formData.username);
    if (usernameErr) errors.username = usernameErr;

    const passwordErr = validators.password(formData.password);
    if (passwordErr) errors.password = passwordErr;

    if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = "Passwords do not match";
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();

    if (!validateForm()) return;

    try {
      await register({
        email: formData.email,
        username: formData.username,
        password: formData.password,
        fullName: formData.fullName || undefined,
      });
      router.push("/onboarding");
    } catch {
      // error is set by context
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {error && (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-950 dark:text-red-400">
          {error}
        </div>
      )}

      <Input
        label="Email"
        type="email"
        placeholder="you@example.com"
        value={formData.email}
        onChange={(e) => updateField("email", e.target.value)}
        error={fieldErrors.email}
        autoComplete="email"
        autoFocus
      />

      <Input
        label="Username"
        type="text"
        placeholder="johndoe"
        value={formData.username}
        onChange={(e) => updateField("username", e.target.value)}
        error={fieldErrors.username}
        autoComplete="username"
      />

      <Input
        label="Full Name"
        type="text"
        placeholder="John Doe"
        value={formData.fullName}
        onChange={(e) => updateField("fullName", e.target.value)}
        autoComplete="name"
      />

      <Input
        label="Password"
        type="password"
        placeholder="Create a strong password"
        value={formData.password}
        onChange={(e) => updateField("password", e.target.value)}
        error={fieldErrors.password}
        autoComplete="new-password"
        hint="At least 8 characters with uppercase, lowercase, and number"
      />

      <Input
        label="Confirm Password"
        type="password"
        placeholder="Repeat your password"
        value={formData.confirmPassword}
        onChange={(e) => updateField("confirmPassword", e.target.value)}
        error={fieldErrors.confirmPassword}
        autoComplete="new-password"
      />

      <Button type="submit" fullWidth isLoading={isLoading}>
        Create account
      </Button>

      <p className="text-center text-sm text-surface-500 dark:text-surface-400">
        Already have an account?{" "}
        <Link
          href={ROUTES.LOGIN}
          className="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400"
        >
          Sign in
        </Link>
      </p>
    </form>
  );
}
