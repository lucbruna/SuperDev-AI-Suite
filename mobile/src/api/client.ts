import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: (data: { username: string; password: string }) => apiClient.post('/api/auth/login', data),
  register: (data: any) => apiClient.post('/api/auth/register', data),
  getMe: () => apiClient.get('/api/auth/me'),
};

export const scannerAPI = {
  runScan: (data: { scanner_type: string; target: string }) => apiClient.post('/api/scanners/run', data),
  getResults: (scanId: string) => apiClient.get(`/api/scanners/results/${scanId}`),
  getHistory: () => apiClient.get('/api/scanners/history'),
};

export const aiAPI = {
  reason: (data: { prompt: string }) => apiClient.post('/api/ai/reason', data),
  plan: (data: { goal: string }) => apiClient.post('/api/ai/plan', data),
  generateCode: (data: any) => apiClient.post('/api/ai/generate-code', data),
  analyzeSecurity: (data: any) => apiClient.post('/api/ai/analyze-security', data),
};

export const enterpriseAPI = {
  getProducts: () => apiClient.get('/api/enterprise/erp/products'),
  getLeads: () => apiClient.get('/api/enterprise/crm/leads'),
  getInvoices: () => apiClient.get('/api/enterprise/finance/invoices'),
};
