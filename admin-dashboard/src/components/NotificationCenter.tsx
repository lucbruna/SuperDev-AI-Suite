import { useEffect, useRef, useState } from 'react';
import { Bell, CheckCheck, Loader2, AlertCircle, Info, CheckCircle2, Zap } from 'lucide-react';
import {
  useSortedNotifications,
  useUnreadCount,
  useMarkNotificationRead,
  useMarkAllNotificationsRead,
} from '../hooks/useNotifications';
import { cn, timeAgo } from '../lib/utils';
import type { AppNotification } from '../types/api';

/** Central de notificações real no header (dropdown). */
export function NotificationCenter() {
  const [open, setOpen] = useState(false);
  const unreadCount = useUnreadCount();
  const notifications = useSortedNotifications();
  const markRead = useMarkNotificationRead();
  const markAllRead = useMarkAllNotificationsRead();
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false);
    };
    document.addEventListener('mousedown', onClickOutside);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onClickOutside);
      document.removeEventListener('keydown', onKey);
    };
  }, []);

  const iconFor = (type: AppNotification['notification_type']) => {
    switch (type) {
      case 'error':
        return <AlertCircle className="h-4 w-4 text-danger-500" />;
      case 'success':
        return <CheckCircle2 className="h-4 w-4 text-success-500" />;
      case 'warning':
        return <Zap className="h-4 w-4 text-warning-500" />;
      default:
        return <Info className="h-4 w-4 text-primary-500" />;
    }
  };

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="relative flex h-9 w-9 items-center justify-center rounded-lg border border-line bg-surface-alt text-ink-muted transition hover:text-ink"
        aria-label={`Notificações${unreadCount > 0 ? ` (${unreadCount} não lidas)` : ''}`}
      >
        <Bell className="h-4 w-4" />
        {unreadCount > 0 && (
          <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-danger-500 px-1 text-[10px] font-bold text-white">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-12 z-40 w-[22rem] max-w-[calc(100vw-2rem)] overflow-hidden rounded-xl border border-line bg-surface shadow-popover animate-slide-up">
          <div className="flex items-center justify-between border-b border-line px-4 py-3">
            <p className="text-sm font-semibold text-ink">Notificações</p>
            <button
              onClick={() => markAllRead.mutate()}
              disabled={unreadCount === 0 || markAllRead.isPending}
              className="flex items-center gap-1 text-xs text-primary-600 transition hover:text-primary-700 disabled:opacity-40"
            >
              {markAllRead.isPending ? (
                <Loader2 className="h-3 w-3 animate-spin" />
              ) : (
                <CheckCheck className="h-3.5 w-3.5" />
              )}
              Marcar todas como lidas
            </button>
          </div>

          <div className="max-h-80 overflow-y-auto scrollbar-thin">
            {notifications.length === 0 ? (
              <div className="flex flex-col items-center gap-2 px-4 py-10 text-center">
                <Bell className="h-6 w-6 text-ink-muted" />
                <p className="text-sm text-ink-muted">Nenhuma notificação</p>
              </div>
            ) : (
              notifications.slice(0, 15).map((n) => (
                <button
                  key={n.id}
                  onClick={() => !n.is_read && markRead.mutate(n.id)}
                  className={cn(
                    'flex w-full items-start gap-3 border-b border-line px-4 py-3 text-left transition last:border-b-0',
                    n.is_read ? 'bg-surface' : 'bg-primary-50/50'
                  )}
                >
                  <span className="mt-0.5 shrink-0">{iconFor(n.notification_type)}</span>
                  <span className="min-w-0 flex-1">
                    <span className="block text-sm font-medium text-ink">{n.title}</span>
                    <span className="mt-0.5 block text-xs text-ink-muted line-clamp-2">{n.message}</span>
                    <span className="mt-1 block text-[11px] text-ink-muted">{timeAgo(n.created_at)}</span>
                  </span>
                  {!n.is_read && <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-primary-500" />}
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
