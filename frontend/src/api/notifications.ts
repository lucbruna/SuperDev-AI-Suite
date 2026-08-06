import apiClient from "./client";

// ---------------------------------------------------------------------------
// Notifications API client — lista, leitura e exclusão de notificações,
// montado em /api/v1/notifications (backend/notifications/router.py).
// ---------------------------------------------------------------------------

const NOTIFICATIONS_BASE = "/notifications";

export interface NotificationItem {
  id?: string;
  title?: string;
  message?: string;
  type?: string;
  read?: boolean;
  created_at?: string;
  [key: string]: unknown;
}

export interface UnreadCount {
  count?: number;
  [key: string]: unknown;
}

export const notificationsApi = {
  async list(unreadOnly = false): Promise<NotificationItem[]> {
    const { data } = await apiClient.get(`${NOTIFICATIONS_BASE}`, {
      params: unreadOnly ? { unread: true } : undefined,
    });
    return data;
  },

  async unreadCount(): Promise<UnreadCount> {
    const { data } = await apiClient.get(`${NOTIFICATIONS_BASE}/unread-count`);
    return data;
  },

  async markRead(id: string): Promise<NotificationItem> {
    const { data } = await apiClient.post(`${NOTIFICATIONS_BASE}/${id}/read`);
    return data;
  },

  async markAllRead(): Promise<Record<string, unknown>> {
    const { data } = await apiClient.post(`${NOTIFICATIONS_BASE}/read-all`);
    return data;
  },

  async remove(id: string): Promise<Record<string, unknown>> {
    const { data } = await apiClient.delete(`${NOTIFICATIONS_BASE}/${id}`);
    return data;
  },
};
