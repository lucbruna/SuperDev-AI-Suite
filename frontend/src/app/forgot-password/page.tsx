"use client";

import { useState } from "react";
import Link from "next/link";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch("/api/v1/auth/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      if (!res.ok) throw new Error("Falha ao enviar email");
      setSent(true);
    } catch {
      setError("Erro ao enviar email de recuperação");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-50 dark:bg-surface-950">
      <div className="w-full max-w-md rounded-xl border bg-white p-8 shadow-lg dark:border-surface-700 dark:bg-surface-900">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Recuperar Senha</h1>
          <p className="mt-2 text-sm text-surface-500">Receba um link para redefinir sua senha</p>
        </div>
        {sent ? (
          <div className="text-center space-y-4">
            <div className="rounded-lg bg-green-50 p-4 text-sm text-green-600 dark:bg-green-900/30 dark:text-green-400">
              Email enviado! Verifique sua caixa de entrada.
            </div>
            <Link href="/login" className="text-primary-600 hover:underline text-sm">Voltar ao login</Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/30 dark:text-red-400">{error}</div>
            )}
            <div>
              <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 w-full rounded-lg border px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:border-surface-600 dark:bg-surface-800"
                placeholder="seu@email.com"
                required
              />
            </div>
            <button type="submit" disabled={loading} className="w-full rounded-lg bg-primary-600 py-2 font-medium text-white hover:bg-primary-700 transition-colors disabled:opacity-50">
              {loading ? "Enviando..." : "Enviar link"}
            </button>
            <p className="text-center text-sm text-surface-500">
              <Link href="/login" className="text-primary-600 hover:underline">Voltar ao login</Link>
            </p>
          </form>
        )}
      </div>
    </div>
  );
}
