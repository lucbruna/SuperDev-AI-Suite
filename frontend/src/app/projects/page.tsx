export default function ProjectsPage() {
  const projects = [
    { id: "1", name: "Sistema ERP", status: "active", description: "Sistema de gestão empresarial" },
    { id: "2", name: "Chatbot IA", status: "active", description: "Chatbot inteligente" },
    { id: "3", name: "API Gateway", status: "draft", description: "Gateway de APIs" },
  ];

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950">
      <header className="border-b bg-white dark:border-surface-700 dark:bg-surface-900">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <h1 className="text-xl font-bold text-primary-600">SuperDev</h1>
          <nav className="flex items-center gap-4">
            <a href="/dashboard" className="text-sm font-medium text-surface-600 hover:text-surface-900 dark:text-surface-400">Dashboard</a>
            <a href="/projects" className="text-sm font-medium text-primary-600">Projetos</a>
            <a href="/agents" className="text-sm font-medium text-surface-600 hover:text-surface-900 dark:text-surface-400">Agentes</a>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Projetos</h2>
          <button className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700">
            + Novo Projeto
          </button>
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <div key={project.id} className="rounded-xl border bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900">
              <div className="flex items-start justify-between">
                <h3 className="font-semibold text-surface-900 dark:text-surface-50">{project.name}</h3>
                <span className={`rounded-full px-2 py-1 text-xs font-medium ${
                  project.status === "active" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
                }`}>
                  {project.status}
                </span>
              </div>
              <p className="mt-2 text-sm text-surface-500">{project.description}</p>
              <button className="mt-4 text-sm font-medium text-primary-600 hover:underline">Abrir →</button>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
