export default function AgentsPage() {
  const agents = [
    { id: "1", name: "Architect Agent", type: "architect", status: "idle", description: "Projeta arquitetura de software" },
    { id: "2", name: "Executor Agent", type: "executor", status: "running", description: "Executa código e tarefas" },
    { id: "3", name: "Reviewer Agent", type: "reviewer", status: "idle", description: "Revisa código automaticamente" },
    { id: "4", name: "Testing Agent", type: "testing", status: "idle", description: "Gera e executa testes" },
  ];

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950">
      <header className="border-b bg-white dark:border-surface-700 dark:bg-surface-900">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <h1 className="text-xl font-bold text-primary-600">SuperDev</h1>
          <nav className="flex items-center gap-4">
            <a href="/dashboard" className="text-sm font-medium text-surface-600 hover:text-surface-900 dark:text-surface-400">Dashboard</a>
            <a href="/projects" className="text-sm font-medium text-surface-600 hover:text-surface-900 dark:text-surface-400">Projetos</a>
            <a href="/agents" className="text-sm font-medium text-primary-600">Agentes</a>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8">
        <h2 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Agentes IA</h2>
        <p className="mt-2 text-surface-600 dark:text-surface-400">Gerencie seus agentes inteligentes</p>

        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          {agents.map((agent) => (
            <div key={agent.id} className="rounded-xl border bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-100 text-primary-600">
                    🤖
                  </div>
                  <div>
                    <h3 className="font-semibold text-surface-900 dark:text-surface-50">{agent.name}</h3>
                    <p className="text-xs text-surface-500">{agent.type}</p>
                  </div>
                </div>
                <span className={`rounded-full px-2 py-1 text-xs font-medium ${
                  agent.status === "running" ? "bg-green-100 text-green-700" : "bg-surface-100 text-surface-600"
                }`}>
                  {agent.status}
                </span>
              </div>
              <p className="mt-3 text-sm text-surface-500">{agent.description}</p>
              <div className="mt-4 flex gap-2">
                <button className="rounded-lg bg-primary-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-primary-700">
                  Iniciar
                </button>
                <button className="rounded-lg border px-3 py-1.5 text-xs font-medium text-surface-600 hover:bg-surface-50">
                  Configurar
                </button>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
