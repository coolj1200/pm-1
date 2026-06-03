import { useCallback, useEffect, useState } from "react";

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
};

export type KanbanUpdate = {
  action: string;
  card_id?: number;
  column_id?: number;
  title?: string;
  details?: string;
  position?: number;
};

const CHAT_HISTORY_KEY = "pm-ai-chat-history";

type ApiChatResponse = {
  response: string;
  kanban_updates?: KanbanUpdate[];
};

const fetchJson = async <T>(path: string, init?: RequestInit): Promise<T> => {
  const response = await fetch(path, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `${response.status} ${response.statusText}`);
  }

  return response.json();
};

export const useAIChat = (
  onApplyUpdates: (updates: KanbanUpdate[] | undefined) => void
) => {
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    try {
      const raw = localStorage.getItem(CHAT_HISTORY_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as ChatMessage[];
        setHistory(Array.isArray(parsed) ? parsed : []);
      }
    } catch {
      setHistory([]);
    }
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    try {
      localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(history));
    } catch {
      // ignore local storage failures
    }
  }, [history]);

  const clearHistory = useCallback(() => {
    setHistory([]);

    if (typeof window !== "undefined") {
      localStorage.removeItem(CHAT_HISTORY_KEY);
    }
  }, []);

  const sendMessage = useCallback(
    async (message: string) => {
      const trimmed = message.trim();
      if (!trimmed) {
        return;
      }

      const userMessage: ChatMessage = {
        role: "user",
        content: trimmed,
        timestamp: new Date().toISOString(),
      };

      const nextHistory = [...history, userMessage];
      setHistory(nextHistory);
      setLoading(true);
      setError(null);

      try {
        const payload = await fetchJson<ApiChatResponse>("/api/ai/chat", {
          method: "POST",
          body: JSON.stringify({
            message: userMessage.content,
            history: nextHistory.map(({ role, content }) => ({ role, content })),
          }),
        });

        const assistantMessage: ChatMessage = {
          role: "assistant",
          content: payload.response,
          timestamp: new Date().toISOString(),
        };

        setHistory([...nextHistory, assistantMessage]);
        onApplyUpdates(payload.kanban_updates);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to reach the AI service");
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [history, onApplyUpdates]
  );

  return {
    history,
    loading,
    error,
    sendMessage,
    clearHistory,
  };
};
