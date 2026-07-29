"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token") || "";

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (password !== confirm) {
      setError("Senhas não conferem");
      return;
    }
    if (password.length < 6) {
      setError("Senha deve ter no mínimo 6 caracteres");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("/api/v1/auth/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, password }),
      });
      if (!res.ok) throw new Error("Falha ao redefinir senha");
      router.push("/login");
    } catch {
      setError("Erro ao redefinir senha. O link pode ter expirado.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-50 dark:bg-surface-950">
      <div className="w-full max-w-md rounded-xl border bg-white p-8 shadow-lg dark:border-surface-700 dark:bg-surface-900">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Redefinir Senha</h1>
          <p className="mt-2 text-sm text-surface-500">Defina uma nova senha para sua conta</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/30 dark:text-red-400">{error}</div>
          )}
          <div>
            <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Nova Senha</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-lg border px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:border-surface-600 dark:bg-surface-800"
              placeholder="••••••••" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Confirmar Senha</label>
            <input type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)}
              className="mt-1 w-full rounded-lg border px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:border-surface-600 dark:bg-surface-800"
              placeholder="••••••••" required />
          </div>
          <button type="submit" disabled={loading} className="w-full rounded-lg bg-primary-600 py-2 font-medium text-white hover:bg-primary-700 transition-colors disabled:opacity-50">
            {loading ? "Redefinindo..." : "Redefinir Senha"}
          </button>
          <p className="text-center text-sm text-surface-500">
            <Link href="/login" className="text-primary-600 hover:underline">Voltar ao login</Link>
          </p>
        </form>
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center">Carregando...</div>}>
      <ResetPasswordForm />
    </Suspense>
  );
}
