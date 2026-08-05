import { NavLink, Outlet } from 'react-router-dom';
import { Shield } from 'lucide-react';
import { cn } from '@/utils';
import { NAV_ADMIN } from '@/constants';
import Header from '@/layout/Header';

export default function AdminLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-surface">
      <aside className="flex w-60 shrink-0 flex-col border-r border-border bg-panel">
        <div className="flex h-14 shrink-0 items-center gap-2 border-b border-border px-4">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-white">
            <Shield className="h-4 w-4" />
          </span>
          <span className="text-sm font-semibold text-content">Administration</span>
        </div>
        <nav className="flex-1 space-y-1 overflow-y-auto p-3">
          {NAV_ADMIN.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'block rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive ? 'bg-primary/10 text-primary' : 'text-subtle hover:bg-surface hover:text-content',
                )
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <Header />
        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-7xl p-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
