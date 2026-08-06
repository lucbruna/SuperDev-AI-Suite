import apiClient from "./client";

// ---------------------------------------------------------------------------
// Scanners API client — scanners de segurança/código, montado em /api/v1/scanners.
// Rotas reais: GET "", POST /{scanner_id}/scan, POST /all/scan.
// ---------------------------------------------------------------------------

const SCANNERS_BASE = "/scanners";

export interface ScannerInfo {
  name?: string;
  description?: string;
  available?: boolean;
  [key: string]: unknown;
}

export interface ScanResult {
  scanner?: string;
  issues?: number;
  status?: string;
  [key: string]: unknown;
}

export const scannersApi = {
  async list(): Promise<ScannerInfo[]> {
    const { data } = await apiClient.get(`${SCANNERS_BASE}`);
    return data;
  },

  async scanAll(target = "."): Promise<ScanResult[]> {
    const { data } = await apiClient.post(`${SCANNERS_BASE}/all/scan`, { target });
    return data;
  },

  async scanOne(scannerId: string, target = "."): Promise<ScanResult> {
    const { data } = await apiClient.post(`${SCANNERS_BASE}/${scannerId}/scan`, { target });
    return data;
  },
};
