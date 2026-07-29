"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/DashboardLayout";
import { useAuthStore } from "@/stores/authStore";

export default function ProfilePage() {
  const { user, updateUser } = useAuthStore();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");

  useEffect(() => {
    if (user) {
      setName(user.fullName || "");
      setEmail(user.email || "");
    }
  }, [user]);

  const handleSave = () => {
    if (name !== user?.fullName) {
      updateUser({ fullName: name });
    }
  };

  return (
    <DashboardLayout>
      <h1 className="mb-6 text-2xl font-bold text-surface-900 dark:text-surface-50">Perfil</h1>

      <div className="max-w-2xl rounded-xl border bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900">
        <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-surface-50">Informações Pessoais</h2>

        <div className="mb-4">
          <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Nome</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Email</label>
          <input
            value={email}
            readOnly
            className="mt-1 w-full rounded-lg border bg-surface-50 px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
          />
        </div>

        <button
          onClick={handleSave}
          className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
        >
          Salvar
        </button>
      </div>
    </DashboardLayout>
  );
}
