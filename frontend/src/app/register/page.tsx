"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authApi } from "@/api/auth";
import { useAuthStore } from "@/stores/authStore";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ email: "", username: "", fullName: "", password: "", confirmPassword: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (form.password !== form.confirmPassword) {
      setError("Senhas não conferem");
      return;
    }
    if (form.password.length < 6) {
      setError("Senha deve ter no mínimo 6 caracteres");
      return;
    }

    setLoading(true);
    try {
      const result = await authApi.register({
        email: form.email,
        username: form.username,
        password: form.password,
        fullName: form.fullName || undefined,
      });
      useAuthStore.getState().login(result.user, result.accessToken, result.refreshToken);
      router.push("/dashboard");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Erro ao criar conta";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-50 p-4 dark:bg-surface-950">
      <div className="w-full max-w-md rounded-xl border bg-white p-8 shadow-lg dark:border-surface-700 dark:bg-surface-900">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Criar Conta</h1>
          <p className="mt-2 text-sm text-surface-500">Cadastre-se no SuperDev</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600">{error}</div>
          )}
          {["email", "username", "fullName", "password", "confirmPassword"].map((field) => (
            <div key={field}>
              <label className="block text-sm font-medium text-surface-700 dark:text-surface-300 capitalize">
                {field === "confirmPassword" ? "Confirmar Senha" : field === "fullName" ? "Nome Completo" : field}
              </label>
              <input
                type={field.includes("password") ? "password" : field === "email" ? "email" : "text"}
                value={(form as any)[field]}
                onChange={(e) => setForm({ ...form, [field]: e.target.value })}
                className="mt-1 w-full rounded-lg border px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:border-surface-600 dark:bg-surface-800"
                placeholder={
                  field === "email" ? "seu@email.com" :
                  field === "username" ? "usuario" :
                  field === "fullName" ? "Seu nome" :
                  field.includes("password") ? "••••••••" : ""
                }
              />
            </div>
          ))}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-primary-600 py-2 font-medium text-white hover:bg-primary-700 disabled:opacity-50"
          >
            {loading ? "Criando conta..." : "Criar Conta"}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-surface-500">
          Já tem conta?{" "}
          <Link href="/login" className="text-primary-600 hover:underline">Entrar</Link>
        </p>
      </div>
    </div>
  );
}
