export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950">
      <header className="border-b bg-white dark:border-surface-700 dark:bg-surface-900">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <h1 className="text-xl font-bold text-primary-600">SuperDev</h1>
          <nav className="flex items-center gap-4">
            <a href="/dashboard" className="text-sm font-medium text-surface-600 hover:text-surface-900 dark:text-surface-400">Dashboard</a>
            <a href="/projects" className="text-sm font-medium text-surface-600 hover:text-surface-900 dark:text-surface-400">Projetos</a>
            <a href="/agents" className="text-sm font-medium text-surface-600 hover:text-surface-900 dark:text-surface-400">Agentes</a>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8">
        <h2 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Dashboard</h2>
        <p className="mt-2 text-surface-600 dark:text-surface-400">Bem-vindo ao SuperDev AI Suite</p>

        <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-xl border bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900">
            <p className="text-sm text-surface-500">Projetos</p>
            <p className="mt-1 text-3xl font-bold text-surface-900 dark:text-surface-50">12</p>
          </div>
          <div className="rounded-xl border bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900">
            <p className="text-sm text-surface-500">Agentes Ativos</p>
            <p className="mt-1 text-3xl font-bold text-green-600">4</p>
          </div>
          <div className="rounded-xl border bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900">
            <p className="text-sm text-surface-500">Workflows</p>
            <p className="mt-1 text-3xl font-bold text-surface-900 dark:text-surface-50">8</p>
          </div>
          <div className="rounded-xl border bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900">
            <p className="text-sm text-surface-500">Plugins</p>
            <p className="mt-1 text-3xl font-bold text-surface-900 dark:text-surface-50">15</p>
          </div>
        </div>
      </main>
    </div>
  );
}
