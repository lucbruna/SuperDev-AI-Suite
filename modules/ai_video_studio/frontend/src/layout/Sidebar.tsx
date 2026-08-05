import { NavLink } from 'react-router-dom';
import { Clapperboard } from 'lucide-react';
import { APP_NAME, APP_VERSION, NAV_MAIN } from '@/constants';
import { roleLabel } from '@/permissions';
import { useAppStore } from '@/store';
import { cn } from '@/utils';
import { Avatar } from '@/ui';

export default function Sidebar() {
  const user = useAppStore((state) => state.user);

  return (
    <aside className="flex w-60 shrink-0 flex-col border-r border-border bg-panel">
      <div className="flex h-14 shrink-0 items-center gap-2 border-b border-border px-4">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-white">
          <Clapperboard className="h-4 w-4" />
        </span>
        <span className="truncate text-sm font-semibold text-content">{APP_NAME}</span>
      </div>
      <nav className="flex-1 space-y-1 overflow-y-auto p-3">
        {NAV_MAIN.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/dashboard'}
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
      <div className="shrink-0 border-t border-border p-3">
        {user ? (
          <div className="flex items-center gap-2">
            <Avatar name={user.name} size="md" />
            <div className="min-w-0">
              <p className="truncate text-sm font-medium text-content">{user.name}</p>
              <p className="text-xs text-subtle">{roleLabel(user.role)}</p>
            </div>
          </div>
        ) : null}
        <p className="mt-2 text-center text-[11px] text-subtle">
          {APP_NAME} v{APP_VERSION}
        </p>
      </div>
    </aside>
  );
}
