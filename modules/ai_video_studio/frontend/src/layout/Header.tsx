import { useMemo, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Bell, Palette } from 'lucide-react';
import { NAV_ADMIN, NAV_MAIN } from '@/constants';
import { roleLabel } from '@/permissions';
import { useAppStore } from '@/store';
import { THEME_OPTIONS } from '@/theme';
import { Avatar, IconButton, Input } from '@/ui';
import Notifications from '@/layout/Notifications';

export default function Header() {
  const { pathname } = useLocation();
  const user = useAppStore((state) => state.user);
  const theme = useAppStore((state) => state.theme);
  const setTheme = useAppStore((state) => state.setTheme);
  const [notifOpen, setNotifOpen] = useState(false);

  const section = useMemo(() => {
    const all = [...NAV_MAIN, ...NAV_ADMIN];
    const match = all.find(
      (item) => pathname === item.path || (item.path !== '/dashboard' && pathname.startsWith(item.path)),
    );
    return match?.label ?? 'Overview';
  }, [pathname]);

  const cycleTheme = () => {
    const index = THEME_OPTIONS.findIndex((t) => t.name === theme);
    const next = THEME_OPTIONS[(index + 1) % THEME_OPTIONS.length];
    setTheme(next.name);
  };

  return (
    <header className="flex h-14 shrink-0 items-center gap-4 border-b border-border bg-panel px-6">
      <h2 className="text-sm font-semibold text-content">{section}</h2>
      <div className="ml-auto flex items-center gap-3">
        <Input className="hidden w-64 md:block" placeholder="Search projects, assets..." aria-label="Search" />
        <IconButton icon={Palette} label="Switch theme" onClick={cycleTheme} />
        <div className="relative">
          <IconButton icon={Bell} label="Notifications" onClick={() => setNotifOpen((value) => !value)} />
          {notifOpen ? <Notifications /> : null}
        </div>
        {user ? (
          <div className="flex items-center gap-2">
            <Avatar name={user.name} size="md" />
            <div className="hidden leading-tight md:block">
              <p className="text-sm font-medium text-content">{user.name}</p>
              <p className="text-xs text-subtle">{roleLabel(user.role)}</p>
            </div>
          </div>
        ) : null}
      </div>
    </header>
  );
}
