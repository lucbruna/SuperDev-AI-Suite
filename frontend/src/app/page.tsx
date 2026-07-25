import Link from "next/link";
import { ROUTES } from "@/constants/routes";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="fixed top-0 z-50 w-full border-b bg-white/80 backdrop-blur-md dark:bg-surface-950/80">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link href="/" className="text-xl font-bold text-primary-600">
            SuperDev
          </Link>
          <nav className="flex items-center gap-4">
            <Link
              href={ROUTES.LOGIN}
              className="text-sm font-medium text-surface-600 hover:text-surface-900 dark:text-surface-400 dark:hover:text-surface-100"
            >
              Sign in
            </Link>
            <Link
              href={ROUTES.REGISTER}
              className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 transition-colors"
            >
              Get Started
            </Link>
          </nav>
        </div>
      </header>

      <main className="flex-1">
        <section className="relative overflow-hidden pt-24 pb-16 sm:pt-32 sm:pb-24">
          <div className="absolute inset-0 bg-grid opacity-30" />
          <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-3xl text-center">
              <h1 className="text-4xl font-bold tracking-tight text-surface-900 sm:text-6xl dark:text-surface-50">
                Supercharge Your
                <span className="text-primary-600 dark:text-primary-400"> Development</span> Workflow
              </h1>
              <p className="mt-6 text-lg leading-8 text-surface-600 dark:text-surface-400">
                An AI-powered suite of tools designed to accelerate your development process.
                Build faster, debug smarter, and deploy with confidence.
              </p>
              <div className="mt-10 flex items-center justify-center gap-4">
                <Link
                  href={ROUTES.REGISTER}
                  className="rounded-lg bg-primary-600 px-8 py-3 text-base font-semibold text-white hover:bg-primary-700 transition-colors shadow-lg"
                >
                  Start Free Trial
                </Link>
                <Link
                  href="#features"
                  className="rounded-lg border border-surface-300 px-8 py-3 text-base font-semibold text-surface-700 hover:bg-surface-50 transition-colors dark:border-surface-600 dark:text-surface-300 dark:hover:bg-surface-800"
                >
                  Learn More
                </Link>
              </div>
            </div>
          </div>
        </section>

        <section id="features" className="py-16 sm:py-24">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-bold tracking-tight text-surface-900 dark:text-surface-50">
                Everything You Need
              </h2>
              <p className="mt-4 text-lg text-surface-600 dark:text-surface-400">
                Powerful tools integrated into one seamless experience.
              </p>
            </div>
            <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
              <FeatureCard
                icon="🧠"
                title="AI-Powered Code Assistant"
                description="Get intelligent code suggestions, refactoring help, and bug detection powered by advanced AI models."
              />
              <FeatureCard
                icon="📝"
                title="Smart Editor"
                description="Feature-rich code editor with syntax highlighting, auto-completion, and multi-cursor editing."
              />
              <FeatureCard
                icon="⚡"
                title="Real-time Collaboration"
                description="Work together with your team in real-time with shared workspaces and live cursors."
              />
              <FeatureCard
                icon="🔄"
                title="Integrated Terminal"
                description="Built-in terminal with multi-session support, split views, and custom configurations."
              />
              <FeatureCard
                icon="📊"
                title="Project Analytics"
                description="Track your project metrics, code quality, and team productivity with detailed dashboards."
              />
              <FeatureCard
                icon="🔒"
                title="Enterprise Security"
                description="Role-based access control, audit logs, and end-to-end encryption for your code."
              />
            </div>
          </div>
        </section>

        <section className="bg-primary-600 py-16 dark:bg-primary-800">
          <div className="mx-auto max-w-7xl px-4 text-center sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold tracking-tight text-white">
              Ready to Transform Your Workflow?
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-lg text-primary-100">
              Join thousands of developers who are already building faster with SuperDev.
            </p>
            <div className="mt-8">
              <Link
                href={ROUTES.REGISTER}
                className="inline-block rounded-lg bg-white px-8 py-3 text-base font-semibold text-primary-600 hover:bg-primary-50 transition-colors shadow-lg"
              >
                Get Started Free
              </Link>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t bg-surface-50 py-8 dark:bg-surface-900 dark:border-surface-800">
        <div className="mx-auto max-w-7xl px-4 text-center text-sm text-surface-500 sm:px-6 lg:px-8">
          <p>&copy; {new Date().getFullYear()} SuperDev AI Suite. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

interface FeatureCardProps {
  icon: string;
  title: string;
  description: string;
}

function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <div className="group rounded-xl border border-surface-200 bg-white p-6 shadow-sm transition-all hover:shadow-md dark:border-surface-700 dark:bg-surface-900">
      <div className="mb-4 text-3xl">{icon}</div>
      <h3 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
        {title}
      </h3>
      <p className="mt-2 text-sm text-surface-600 dark:text-surface-400">
        {description}
      </p>
    </div>
  );
}
