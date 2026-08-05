import { NavLink, Outlet } from 'react-router-dom';
import { AudioLines, UserRound } from 'lucide-react';
import { cn } from '@/utils';
import Header from '@/layout/Header';

const studioNav = [
  { label: 'Avatar Studio', path: '/avatar', icon: UserRound },
  { label: 'Voice Studio', path: '/voice', icon: AudioLines },
];

export default function StudioLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-surface">
      <aside className="flex w-52 shrink-0 flex-col border-r border-border bg-panel">
        <p className="px-4 pt-5 pb-2 text-[11px] font-semibold uppercase tracking-wider text-subtle">Studio</p>
        <nav className="space-y-1 p-3 pt-0">
          {studioNav.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive ? 'bg-primary/10 text-primary' : 'text-subtle hover:bg-surface hover:text-content',
                )
              }
            >
              <item.icon className="h-4 w-4" />
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
