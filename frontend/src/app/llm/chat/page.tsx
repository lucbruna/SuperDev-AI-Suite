"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { DashboardLayout } from "@/components/DashboardLayout";
import { llmApi, type LLMProviderSummary } from "@/api/llm";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ChatEntry {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: number;
  provider?: string;
  model?: string;
}

// ---------------------------------------------------------------------------
// Message Bubble
// ---------------------------------------------------------------------------

function MessageBubble({ message }: { message: ChatEntry }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div className={`max-w-[80%] ${isUser ? "order-1" : "order-1"}`}>
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
            isUser
              ? "bg-primary-600 text-white rounded-br-md"
              : "bg-surface-100 text-surface-900 dark:bg-surface-800 dark:text-surface-100 rounded-bl-md"
          }`}
        >
          <pre className="whitespace-pre-wrap font-sans">{message.content}</pre>
        </div>
        <div className={`mt-1 flex gap-2 text-xs text-surface-400 ${isUser ? "justify-end" : "justify-start"}`}>
          {message.provider && <span>{message.provider}</span>}
          {message.model && <span>{message.model}</span>}
          <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Model/Provider Selector
// ---------------------------------------------------------------------------

function ModelSelector({
  providers,
  selectedProvider,
  selectedModel,
  models,
  onProviderChange,
  onModelChange,
}: {
  providers: LLMProviderSummary[];
  selectedProvider: string;
  selectedModel: string;
  models: string[];
  onProviderChange: (p: string) => void;
  onModelChange: (m: string) => void;
}) {
  return (
    <div className="flex items-center gap-2 border-b border-surface-200 bg-white px-4 py-2 dark:border-surface-700 dark:bg-surface-900">
      <select
        value={selectedProvider}
        onChange={(e) => onProviderChange(e.target.value)}
        className="rounded-lg border border-surface-200 bg-white px-3 py-1.5 text-xs font-medium text-surface-700 dark:border-surface-600 dark:bg-surface-800 dark:text-surface-200"
      >
        {providers.length === 0 && <option value="">Automático</option>}
        {providers
          .filter((p) => p.api_key_configured)
          .map((p) => (
            <option key={p.name} value={p.name}>
              {p.name.charAt(0).toUpperCase() + p.name.slice(1)}
            </option>
          ))}
      </select>

      <select
        value={selectedModel}
        onChange={(e) => onModelChange(e.target.value)}
        className="flex-1 rounded-lg border border-surface-200 bg-white px-3 py-1.5 text-xs text-surface-700 dark:border-surface-600 dark:bg-surface-800 dark:text-surface-200"
      >
        {models.map((m) => (
          <option key={m} value={m}>
            {m}
          </option>
        ))}
      </select>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Chat Page
// ---------------------------------------------------------------------------

export default function LLMChatPage() {
  const [messages, setMessages] = useState<ChatEntry[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [providers, setProviders] = useState<LLMProviderSummary[]>([]);
  const [selectedProvider, setSelectedProvider] = useState("");
  const [models, setModels] = useState<string[]>(["Automático"]);
  const [selectedModel, setSelectedModel] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [temperature, setTemperature] = useState(0.7);
  const abortRef = useRef<AbortController | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  // Load providers
  const loadProviders = useCallback(async () => {
    try {
      const data = await llmApi.listProviders();
      const configured = data.filter((p) => p.api_key_configured);
      setProviders(configured);
      if (configured.length > 0 && !configured.some((provider) => provider.name === selectedProvider)) {
        setSelectedProvider(configured[0].name);
      }
    } catch {
      // Silently fail, user will see error when trying to send
    }
  }, [selectedProvider]);

  useEffect(() => {
    loadProviders();
  }, [loadProviders]);

  // Load models when provider changes
  useEffect(() => {
    if (!selectedProvider) {
      setModels(["Automático"]);
      setSelectedModel("");
      return;
    }
    llmApi
      .listModels(selectedProvider)
      .then((data) => {
        const providerModels = data[selectedProvider]?.models || [];
        const modelIds = providerModels.map((m: any) => m.id);
        setModels(modelIds);
        setSelectedModel((current) =>
          modelIds.length > 0 && !modelIds.includes(current)
            ? modelIds[0]
            : current
        );
      })
      .catch(() => {
        setModels([`${selectedProvider}-default`]);
      });
  }, [selectedProvider]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || isStreaming) return;

    const userMessage: ChatEntry = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text,
      timestamp: Date.now(),
      provider: selectedProvider,
      model: selectedModel,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setError(null);
    setIsStreaming(true);
    setStreamingContent("");

    abortRef.current = new AbortController();

    try {
      const assistantId = `assistant-${Date.now()}`;
      const assistantEntry: ChatEntry = {
        id: assistantId,
        role: "assistant",
        content: "",
        timestamp: Date.now(),
        provider: selectedProvider,
        model: selectedModel,
      };
      setMessages((prev) => [...prev, assistantEntry]);

      const response = await llmApi.agentChat({
        message: text,
        provider: selectedProvider || undefined,
        model: selectedModel || undefined,
        temperature,
      });
      const toolSummary = response.tool_calls.length
        ? `\n\nFerramentas usadas: ${response.tool_calls.map((call) => call.name).join(", ")}`
        : "";
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, content: `${response.content}${toolSummary}`, timestamp: Date.now() }
            : m
        )
      );
      setIsStreaming(false);
    } catch (err: any) {
      if (err.name === "AbortError") {
        setMessages((prev) =>
          prev.map((m) =>
            m.role === "assistant" && !m.content
              ? { ...m, content: m.content + streamingContent + "\n\n[Stream cancelled]" }
              : m
          )
        );
      } else {
        setError(err?.message || "Falha ao enviar mensagem");
        setMessages((prev) =>
          prev.map((m) =>
            m.role === "assistant" && !m.content
              ? { ...m, content: `[Error: ${err?.message || "Unknown error"}]` }
              : m
          )
        );
      }
      setIsStreaming(false);
      setStreamingContent("");
    }
  };

  const stopStreaming = () => {
    abortRef.current?.abort();
    setIsStreaming(false);
  };

  const clearChat = () => {
    setMessages([]);
    setStreamingContent("");
    setError(null);
  };

  const finalMessages = [
    ...messages,
    ...(isStreaming && streamingContent
      ? [
          {
            id: "streaming",
            role: "assistant" as const,
            content: streamingContent,
            timestamp: Date.now(),
            provider: selectedProvider,
            model: selectedModel,
          },
        ]
      : []),
  ];

  // O backend escolhe o provider configurado quando provider/model não são enviados.
  // A descoberta de providers é opcional e não deve bloquear o chat.
  const hasConfig = true;

  return (
    <DashboardLayout>
      <div className="flex h-[calc(100vh-4rem)] flex-col">
        {/* Model selector */}
        <ModelSelector
          providers={providers}
          selectedProvider={selectedProvider}
          selectedModel={selectedModel}
          models={models}
          onProviderChange={setSelectedProvider}
          onModelChange={setSelectedModel}
        />

        {/* Messages */}
        <div className="flex-1 overflow-y-auto bg-surface-50 px-4 py-6 dark:bg-surface-950">
          {finalMessages.length === 0 && !error && (
            <div className="flex h-full items-center justify-center">
              <div className="max-w-md text-center">
                <div className="mb-4 text-5xl">💬</div>
                <h2 className="mb-2 text-xl font-semibold text-surface-700 dark:text-surface-200">
                  LLM Chat
                </h2>
                <p className="text-sm text-surface-500">
                  {hasConfig
                    ? "Digite uma mensagem abaixo para começar a conversar com os modelos de IA."
                    : "Configure uma API key nas variáveis de ambiente para começar."}
                </p>
              </div>
            </div>
          )}

          <div className="mx-auto max-w-3xl">
            {finalMessages.map((m) => (
              <MessageBubble key={m.id} message={m} />
            ))}
            {isStreaming && !streamingContent && (
              <div className="flex items-center gap-2 text-sm text-surface-400">
                <div className="h-2 w-2 animate-bounce rounded-full bg-primary-400" />
                <div className="h-2 w-2 animate-bounce rounded-full bg-primary-400" style={{ animationDelay: "0.1s" }} />
                <div className="h-2 w-2 animate-bounce rounded-full bg-primary-400" style={{ animationDelay: "0.2s" }} />
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {error && (
            <div className="mx-auto mt-4 max-w-3xl">
              <div className="rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
                {error}
              </div>
            </div>
          )}
        </div>

        {/* Input area */}
        <div className="border-t border-surface-200 bg-white p-4 dark:border-surface-700 dark:bg-surface-900">
          <div className="mx-auto flex max-w-3xl items-end gap-3">
            <div className="flex-1">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder={hasConfig ? "Digite sua mensagem..." : "Nenhum provider configurado..."}
                disabled={!hasConfig || isStreaming}
                rows={2}
                className="w-full resize-none rounded-xl border border-surface-200 bg-surface-50 px-4 py-3 text-sm text-surface-900 placeholder-surface-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100 dark:placeholder-surface-500 disabled:opacity-50"
              />
            </div>

            <div className="flex items-center gap-2">
              {isStreaming ? (
                <button
                  onClick={stopStreaming}
                  className="rounded-xl bg-red-600 px-4 py-3 text-sm font-medium text-white transition-colors hover:bg-red-500"
                >
                  Stop
                </button>
              ) : (
                <button
                  onClick={sendMessage}
                  disabled={!input.trim() || !hasConfig}
                  className="rounded-xl bg-primary-600 px-4 py-3 text-sm font-medium text-white transition-colors hover:bg-primary-500 disabled:opacity-50"
                >
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </button>
              )}

              <button
                onClick={clearChat}
                disabled={messages.length === 0}
                className="rounded-xl border border-surface-200 px-3 py-3 text-sm text-surface-500 transition-colors hover:bg-surface-50 dark:border-surface-600 dark:hover:bg-surface-800 disabled:opacity-30"
                title="Limpar conversa"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>

          <div className="mx-auto mt-2 flex max-w-3xl items-center justify-between px-1">
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2 text-xs text-surface-400">
                Temp:
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  className="w-20"
                />
                <span className="w-8 text-center font-mono">{temperature.toFixed(1)}</span>
              </label>
            </div>
            <p className="text-xs text-surface-400">
              Enter para enviar · Shift+Enter para nova linha
            </p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
