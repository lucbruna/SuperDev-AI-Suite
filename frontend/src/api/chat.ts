import axios from 'axios';
import { ChatRequest, ChatResponse, Conversation, Message } from '../types/chat';

const api = axios.create({
  baseURL: '/api/chat',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function sendMessage(req: ChatRequest): Promise<ChatResponse> {
  const { data } = await api.post<ChatResponse>('/send', req);
  return data;
}

export async function getConversations(): Promise<Conversation[]> {
  const { data } = await api.get<Conversation[]>('/conversations');
  return data;
}

export async function getConversation(id: string): Promise<Conversation> {
  const { data } = await api.get<Conversation>(`/conversations/${id}`);
  return data;
}

export async function createConversation(params: {
  title?: string;
  model?: string;
  provider?: string;
}): Promise<Conversation> {
  const { data } = await api.post<Conversation>('/conversations', params);
  return data;
}

export async function deleteConversation(id: string): Promise<void> {
  await api.delete(`/conversations/${id}`);
}
