"use client";

import { useState } from "react";
import Link from "next/link";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Register:", { name, email, password });
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-50 dark:bg-surface-950">
      <div className="w-full max-w-md rounded-xl border bg-white p-8 shadow-lg dark:border-surface-700 dark:bg-surface-900">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Criar Conta</h1>
          <p className="mt-2 text-sm text-surface-500">Comece a usar o SuperDev</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Nome</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="mt-1 w-full rounded-lg border px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:border-surface-600 dark:bg-surface-800"
              placeholder="Seu nome"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-lg border px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:border-surface-600 dark:bg-surface-800"
              placeholder="seu@email.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Senha</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-lg border px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:border-surface-600 dark:bg-surface-800"
              placeholder="••••••••"
            />
          </div>
          <button
            type="submit"
            className="w-full rounded-lg bg-primary-600 py-2 font-medium text-white hover:bg-primary-700 transition-colors"
          >
            Criar Conta
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
