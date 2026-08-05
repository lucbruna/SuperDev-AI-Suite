import { CheckCheck } from 'lucide-react';
import { useAppStore } from '@/store';
import { cn, timeAgo } from '@/utils';
import { Badge, Button } from '@/ui';

const kindTone = {
  info: 'info',
  success: 'success',
  warning: 'warning',
  error: 'danger',
} as const;

export default function Notifications() {
  const notifications = useAppStore((state) => state.notifications);
  const markRead = useAppStore((state) => state.markNotificationRead);
  const markAll = useAppStore((state) => state.markAllNotificationsRead);
  const unread = notifications.filter((n) => !n.read).length;

  return (
    <div className="absolute right-0 top-full z-50 mt-2 w-80 overflow-hidden rounded-xl border border-border bg-panel shadow-lg">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <p className="text-sm font-semibold text-content">Notifications</p>
        <Button variant="ghost" size="sm" onClick={markAll} disabled={unread === 0}>
          <CheckCheck className="h-4 w-4" /> Mark all read
        </Button>
      </div>
      <div className="max-h-80 overflow-y-auto">
        {notifications.length === 0 ? (
          <p className="px-4 py-8 text-center text-sm text-subtle">You&apos;re all caught up.</p>
        ) : (
          notifications.map((n) => (
            <button
              key={n.id}
              type="button"
              onClick={() => markRead(n.id)}
              className={cn(
                'block w-full border-b border-border px-4 py-3 text-left transition-colors hover:bg-surface',
                !n.read && 'bg-primary/5',
              )}
            >
              <div className="flex items-start gap-2">
                <Badge variant={kindTone[n.kind]} className="mt-0.5">
                  {n.kind}
                </Badge>
                <div className="min-w-0">
                  <p className="text-sm font-medium text-content">{n.title}</p>
                  {n.body ? <p className="mt-0.5 text-xs text-subtle">{n.body}</p> : null}
                  <p className="mt-1 text-[11px] text-subtle">{timeAgo(n.createdAt)}</p>
                </div>
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
}
