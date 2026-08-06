import apiClient from "./client";

// ---------------------------------------------------------------------------
// Backup API client — backups de banco/arquivos/completo e restauração,
// montado em /api/v1/backup (backend/backup/router.py).
// ---------------------------------------------------------------------------

const BACKUP_BASE = "/backup";

export interface BackupEntry {
  id?: string;
  kind?: string;
  path?: string;
  size_bytes?: number;
  created_at?: string;
  [key: string]: unknown;
}

export interface BackupStats {
  total?: number;
  last_backup?: string;
  [key: string]: unknown;
}

export const backupApi = {
  async list(): Promise<BackupEntry[]> {
    const { data } = await apiClient.get(`${BACKUP_BASE}`);
    return data;
  },

  async database(): Promise<BackupEntry> {
    const { data } = await apiClient.post(`${BACKUP_BASE}/database`);
    return data;
  },

  async files(): Promise<BackupEntry> {
    const { data } = await apiClient.post(`${BACKUP_BASE}/files`);
    return data;
  },

  async full(): Promise<BackupEntry> {
    const { data } = await apiClient.post(`${BACKUP_BASE}/full`);
    return data;
  },

  async restore(backupId: string): Promise<Record<string, unknown>> {
    const { data } = await apiClient.post(`${BACKUP_BASE}/restore`, { id: backupId });
    return data;
  },

  async stats(): Promise<BackupStats> {
    const { data } = await apiClient.get(`${BACKUP_BASE}/stats`);
    return data;
  },
};
