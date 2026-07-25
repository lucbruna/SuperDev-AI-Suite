"use client";

import { useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Input } from "@/components/inputs/Input";
import { Button } from "@/components/buttons/Button";
import { useAuth } from "@/hooks/useAuth";
import { ROUTES } from "@/constants/routes";

export function LoginForm() {
  const router = useRouter();
  const { login, isLoading, error, clearError } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setValidationError(null);
    clearError();

    if (!email.trim()) {
      setValidationError("Email is required");
      return;
    }
    if (!password) {
      setValidationError("Password is required");
      return;
    }

    try {
      await login({ email, password, rememberMe });
      router.push(ROUTES.DASHBOARD);
    } catch {
      // error is set by context
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {(validationError || error) && (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-950 dark:text-red-400">
          {validationError || error}
        </div>
      )}

      <Input
        label="Email"
        type="email"
        placeholder="you@example.com"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        autoComplete="email"
        autoFocus
      />

      <Input
        label="Password"
        type="password"
        placeholder="Enter your password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        autoComplete="current-password"
      />

      <div className="flex items-center justify-between">
        <label className="flex items-center gap-2 text-sm text-surface-600 dark:text-surface-400">
          <input
            type="checkbox"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
            className="rounded border-surface-300 text-primary-600 focus:ring-primary-500 dark:border-surface-600"
          />
          Remember me
        </label>
        <Link
          href={ROUTES.FORGOT_PASSWORD}
          className="text-sm font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400"
        >
          Forgot password?
        </Link>
      </div>

      <Button type="submit" fullWidth isLoading={isLoading}>
        Sign in
      </Button>

      <p className="text-center text-sm text-surface-500 dark:text-surface-400">
        Don&apos;t have an account?{" "}
        <Link
          href={ROUTES.REGISTER}
          className="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400"
        >
          Sign up
        </Link>
      </p>
    </form>
  );
}
