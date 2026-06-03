"use client";

import clsx from "clsx";
import { useMemo, useState, type FormEvent } from "react";
import type { ChatMessage } from "@/lib/useAIChat";

const formatTimestamp = (timestamp: string) => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
};

type AIChatSidebarProps = {
  history: ChatMessage[];
  loading: boolean;
  error: string | null;
  onSend: (message: string) => Promise<void>;
  onClear: () => void;
};

export const AIChatSidebar = ({
  history,
  loading,
  error,
  onSend,
  onClear,
}: AIChatSidebarProps) => {
  const [draft, setDraft] = useState("");
  const [isOpen, setIsOpen] = useState(true);

  const empty = history.length === 0;
  const lastMessage = history[history.length - 1];
  const buttonLabel = isOpen ? "Collapse chat" : "Open chat";

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!draft.trim()) {
      return;
    }

    await onSend(draft);
    setDraft("");
  };

  const summary = useMemo(() => {
    if (empty) {
      return "Ask the AI to create, move, or update a card.";
    }
    return `${lastMessage?.role === "assistant" ? "AI:" : "You:"} ${lastMessage?.content.slice(0, 40)}`;
  }, [empty, lastMessage]);

  return (
    <aside className="flex flex-col rounded-[32px] border border-[var(--stroke)] bg-white/95 shadow-[var(--shadow)] transition">
      <div className="flex items-center justify-between gap-3 border-b border-[var(--stroke)] bg-[var(--surface)] px-5 py-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[var(--gray-text)]">AI Assistant</p>
          <p className="mt-2 text-sm font-semibold text-[var(--navy-dark)]">Chat with the board</p>
        </div>
        <button
          type="button"
          aria-expanded={isOpen}
          onClick={() => setIsOpen((open) => !open)}
          className="rounded-full border border-[var(--stroke)] px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--navy-dark)] transition hover:border-[var(--primary-blue)] hover:text-[var(--primary-blue)]"
        >
          {buttonLabel}
        </button>
      </div>

      {isOpen ? (
        <div className="flex min-h-[560px] flex-col px-5 py-4">
          <div className="mb-4 rounded-3xl border border-[var(--stroke)] bg-[var(--surface-strong)] p-4 text-sm text-[var(--gray-text)]">
            {summary}
          </div>

          <div
            role="log"
            aria-live="polite"
            className="mb-4 flex-1 space-y-3 overflow-y-auto rounded-3xl border border-[var(--stroke)] bg-white p-4 shadow-[var(--shadow)]"
          >
            {empty ? (
              <p className="text-sm text-[var(--gray-text)]">Start by asking the AI a board question.</p>
            ) : (
              history.map((message, index) => (
                <div
                  key={`${message.role}-${index}`}
                  className={clsx(
                    "rounded-3xl p-4",
                    message.role === "user"
                      ? "bg-[var(--surface)] self-end text-[var(--navy-dark)]"
                      : "bg-[var(--surface-strong)] self-start text-[var(--navy-dark)]"
                  )}
                >
                  <div className="mb-2 text-xs uppercase tracking-[0.2em] text-[var(--gray-text)]">
                    {message.role === "user" ? "You" : "AI"}
                  </div>
                  <div className="whitespace-pre-wrap text-sm leading-6">{message.content}</div>
                  <div className="mt-3 text-[11px] uppercase tracking-[0.2em] text-[var(--gray-text)]">
                    {formatTimestamp(message.timestamp)}
                  </div>
                </div>
              ))
            )}
          </div>

          {error ? (
            <div className="mb-4 rounded-3xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              <p className="font-semibold">AI chat error</p>
              <p>{error}</p>
            </div>
          ) : null}

          <form className="space-y-3" onSubmit={handleSubmit}>
            <label htmlFor="ai-chat-input" className="sr-only">
              Type a message for the AI
            </label>
            <textarea
              id="ai-chat-input"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              rows={4}
              placeholder="Ask the AI to update the board..."
              className="w-full rounded-3xl border border-[var(--stroke)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)] focus:ring-2 focus:ring-[rgba(32,157,215,0.15)]"
              aria-label="Chat message"
            />
            <div className="flex flex-wrap items-center justify-between gap-3">
              <button
                type="submit"
                disabled={loading}
                className="inline-flex items-center justify-center rounded-full bg-[var(--primary-blue)] px-5 py-3 text-xs font-semibold uppercase tracking-[0.2em] text-white transition hover:bg-[#1877ab] disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? "Thinking..." : "Send"}
              </button>
              <button
                type="button"
                onClick={onClear}
                className="inline-flex items-center justify-center rounded-full border border-[var(--stroke)] px-4 py-3 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--navy-dark)] transition hover:border-[var(--primary-blue)] hover:text-[var(--primary-blue)]"
              >
                Clear conversation
              </button>
            </div>
          </form>
        </div>
      ) : (
        <div className="p-5 text-sm text-[var(--gray-text)]">{summary}</div>
      )}
    </aside>
  );
};
