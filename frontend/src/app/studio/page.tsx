"use client";

import { DashboardLayout } from "@/components/DashboardLayout";

/**
 * Studio page — visual workflow/node editor.
 *
 * O backend ainda não implementa o módulo de Studio (o WebSocket /studio/ws
 * não está ativo). A página exibe um estado honesto de "em construção" em vez
 * de tentar conectar a um endpoint inexistente.
 */
export default function StudioPage() {
  return (
    <DashboardLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Studio</h1>
          <p className="mt-1 text-sm text-surface-500">Editor visual de workflows e nós</p>
        </div>
      </div>

      <div className="rounded-xl border bg-white p-12 text-center shadow-sm dark:border-surface-700 dark:bg-surface-900">
        <div className="mb-4 text-5xl">🎨</div>
        <h2 className="mb-2 text-xl font-semibold text-surface-700 dark:text-surface-200">Studio</h2>
        <p className="mb-4 text-sm text-surface-500 max-w-md mx-auto">
          O Studio permitirá criar e editar workflows visualmente com um canvas de nós interativo.
        </p>
        <div className="mx-auto max-w-md rounded-lg bg-surface-50 p-4 text-sm text-surface-500 dark:bg-surface-800">
          Em construção — o suporte a WebSocket do Studio ainda não está disponível no backend.
        </div>
      </div>
    </DashboardLayout>
  );
}
