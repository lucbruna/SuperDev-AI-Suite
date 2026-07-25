import { useState, useCallback, useRef, useEffect } from 'react';
import { Conversation, Message, StreamChunk } from '../types/chat';
import * as chatApi from '../api/chat';

interface UseChatReturn {
  conversations: Conversation[];
  activeConversation: Conversation | null;
  isStreaming: boolean;
  sendMessage: (text: string) => Promise<void>;
  streamMessage: (text: string, onChunk: (chunk: StreamChunk) => void) => Promise<void>;
  createConversation: (title?: string) => Promise<Conversation>;
  deleteConversation: (id: string) => Promise<void>;
  setActiveConversation: (conv: Conversation | null) => void;
  stopStreaming: () => void;
  loading: boolean;
  error: string | null;
}

export function useChat(): UseChatReturn {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversation, setActiveConversation] = useState<Conversation | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    loadConversations();
    return () => {
      wsRef.current?.close();
    };
  }, []);

  const loadConversations = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await chatApi.getConversations();
      setConversations(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to load conversations');
    } finally {
      setLoading(false);
    }
  }, []);

  const sendMessage = useCallback(async (text: string) => {
    if (!activeConversation) return;
    setError(null);
    try {
      const userMessage: Message = {
        id: `temp-${Date.now()}`,
        role: 'user',
        content: text,
        timestamp: Date.now(),
        model: activeConversation.model,
        provider: activeConversation.provider,
      };
      const updated: Conversation = {
        ...activeConversation,
        messages: [...activeConversation.messages, userMessage],
      };
      setActiveConversation(updated);
      setConversations((prev) =>
        prev.map((c) => (c.id === updated.id ? updated : c))
      );

      await chatApi.sendMessage({
        conversation_id: activeConversation.id,
        message: text,
        model: activeConversation.model,
        provider: activeConversation.provider,
      });
    } catch (err: any) {
      setError(err?.message || 'Failed to send message');
    }
  }, [activeConversation]);

  const streamMessage = useCallback(
    async (text: string, onChunk: (chunk: StreamChunk) => void) => {
      if (!activeConversation) return;
      setError(null);
      setIsStreaming(true);

      try {
        const token = localStorage.getItem('auth_token');
        const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
        const ws = new WebSocket(
          `${protocol}://${window.location.host}/api/chat/stream?token=${token}`
        );
        wsRef.current = ws;

        ws.onopen = () => {
          ws.send(
            JSON.stringify({
              conversation_id: activeConversation.id,
              message: text,
              model: activeConversation.model,
              provider: activeConversation.provider,
            })
          );
        };

        ws.onmessage = (event) => {
          const chunk: StreamChunk = JSON.parse(event.data);
          onChunk(chunk);
          if (chunk.finish_reason) {
            setIsStreaming(false);
            ws.close();
          }
        };

        ws.onerror = () => {
          setError('WebSocket connection error');
          setIsStreaming(false);
        };

        ws.onclose = () => {
          setIsStreaming(false);
          wsRef.current = null;
          loadConversations();
        };
      } catch (err: any) {
        setError(err?.message || 'Failed to stream message');
        setIsStreaming(false);
      }
    },
    [activeConversation, loadConversations]
  );

  const createConversation = useCallback(
    async (title?: string) => {
      setError(null);
      try {
        const conv = await chatApi.createConversation({ title });
        setConversations((prev) => [conv, ...prev]);
        setActiveConversation(conv);
        return conv;
      } catch (err: any) {
        setError(err?.message || 'Failed to create conversation');
        throw err;
      }
    },
    []
  );

  const deleteConversation = useCallback(
    async (id: string) => {
      setError(null);
      try {
        await chatApi.deleteConversation(id);
        setConversations((prev) => prev.filter((c) => c.id !== id));
        if (activeConversation?.id === id) {
          setActiveConversation(null);
        }
      } catch (err: any) {
        setError(err?.message || 'Failed to delete conversation');
      }
    },
    [activeConversation]
  );

  const stopStreaming = useCallback(() => {
    wsRef.current?.close();
    setIsStreaming(false);
  }, []);

  return {
    conversations,
    activeConversation,
    isStreaming,
    sendMessage,
    streamMessage,
    createConversation,
    deleteConversation,
    setActiveConversation,
    stopStreaming,
    loading,
    error,
  };
}
