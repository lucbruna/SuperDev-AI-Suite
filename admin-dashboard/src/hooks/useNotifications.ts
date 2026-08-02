import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useMemo } from 'react';
import { notificationsApi, withFallback } from '../services/api';
import type { AppNotification } from '../types/api';

export const notificationsKeys = {
  all: ['notifications'] as const,
  list: (unreadOnly: boolean) => ['notifications', 'list', unreadOnly] as const,
  unread: ['notifications', 'unread-count'] as const,
};

/** Lista de notificações com fallback defensivo. */
export function useNotifications(unreadOnly = false) {
  const query = useQuery({
    queryKey: notificationsKeys.list(unreadOnly),
    queryFn: () => withFallback(notificationsApi.list(unreadOnly), []),
    staleTime: 1000 * 30,
  });
  return { ...query, notifications: query.data ?? [] };
}

/** Contagem de não lidas. */
export function useUnreadCount() {
  const query = useQuery({
    queryKey: notificationsKeys.unread,
    queryFn: () => withFallback(notificationsApi.unreadCount(), { count: 0 }),
    staleTime: 1000 * 15,
    refetchInterval: 1000 * 30,
  });
  return query.data?.count ?? 0;
}

/** Marca uma notificação como lida e invalida o cache. */
export function useMarkNotificationRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => notificationsApi.markRead(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: notificationsKeys.all });
    },
  });
}

/** Marca todas como lidas. */
export function useMarkAllNotificationsRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => notificationsApi.markAllRead(),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: notificationsKeys.all });
    },
  });
}

/** Notificações ordenadas por data (mais recentes primeiro). */
export function useSortedNotifications(unreadOnly = false): AppNotification[] {
  const { notifications } = useNotifications(unreadOnly);
  return useMemo(
    () =>
      [...notifications].sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      ),
    [notifications]
  );
}
