"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/DashboardLayout";
import { usersApi } from "@/api/users";

export default function AdminUsersPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    usersApi
      .getUsers()
      .then((res: any) => setUsers(Array.isArray(res) ? res : res.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <DashboardLayout>
      <h1 className="mb-6 text-2xl font-bold text-surface-900 dark:text-surface-50">Usuários</h1>

      <div className="rounded-xl border bg-white shadow-sm dark:border-surface-700 dark:bg-surface-900">
        {loading ? (
          <p className="p-6 text-surface-400">Carregando...</p>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="border-b dark:border-surface-700">
              <tr className="bg-surface-50 dark:bg-surface-800">
                <th className="px-4 py-3 font-medium text-surface-600">Email</th>
                <th className="px-4 py-3 font-medium text-surface-600">Usuário</th>
                <th className="px-4 py-3 font-medium text-surface-600">Criado em</th>
              </tr>
            </thead>
            <tbody className="divide-y dark:divide-surface-700">
              {users.map((u: any) => (
                <tr key={u.id} className="hover:bg-surface-50 dark:hover:bg-surface-800/50">
                  <td className="px-4 py-3 text-surface-900 dark:text-surface-100">{u.email}</td>
                  <td className="px-4 py-3 text-surface-600">{u.username || "-"}</td>
                  <td className="px-4 py-3 text-surface-500">{u.createdAt ? new Date(u.createdAt).toLocaleDateString() : "-"}</td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr><td colSpan={3} className="px-4 py-8 text-center text-surface-400">Nenhum usuário encontrado</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </DashboardLayout>
  );
}
