export type MessageRole = 'user' | 'assistant' | 'system';

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: number;
  model: string;
  provider: string;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  model: string;
  provider: string;
  created_at: number;
  updated_at: number;
}

export interface ChatRequest {
  conversation_id?: string;
  message: string;
  model: string;
  provider: string;
  temperature?: number;
  max_tokens?: number;
}

export interface ChatResponse {
  id: string;
  message: Message;
  conversation_id: string;
}

export interface StreamChunk {
  delta: string;
  finish_reason: 'stop' | 'length' | 'error' | null;
  conversation_id?: string;
  message_id?: string;
}
