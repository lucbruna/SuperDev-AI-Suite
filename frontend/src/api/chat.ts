import apiClient from '@/api/client';
import type { ChatRequest, ChatResponse, Conversation, StreamChunk } from '@/types/chat';

export async function getConversations(): Promise<Conversation[]> {
  const { data } = await apiClient.get<Conversation[]>('/chat/conversations');
  return data;
}

export async function createConversation(params?: { title?: string }): Promise<Conversation> {
  const { data } = await apiClient.post<Conversation>('/chat/conversations', params);
  return data;
}

export async function sendMessage(params: ChatRequest): Promise<ChatResponse> {
  const { data } = await apiClient.post<ChatResponse>('/chat/messages', params);
  return data;
}

export async function deleteConversation(id: string): Promise<void> {
  await apiClient.delete(`/chat/conversations/${id}`);
}
