import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { useAIChat } from "@/lib/useAIChat";

type Props = { onApplyUpdates: (updates: unknown) => void };

const TestComponent = ({ onApplyUpdates }: Props) => {
  const { history, loading, error, sendMessage, clearHistory } = useAIChat(onApplyUpdates);

  return (
    <div>
      <button type="button" onClick={() => void sendMessage("Hello AI")}>Send</button>
      <button type="button" onClick={() => clearHistory()}>Clear</button>
      <div>{loading ? "loading" : "idle"}</div>
      <div>{error ?? "no-error"}</div>
      <div data-testid="history-count">{history.length}</div>
      {history.map((message, index) => (
        <div key={index}>{message.role}: {message.content}</div>
      ))}
    </div>
  );
};

describe("useAIChat", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("sends a user message and appends the assistant response", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        response: "Ok, I added a card.",
        kanban_updates: [{ action: "create_card", column_id: 1, title: "New AI task" }],
      }),
    }));
    vi.stubGlobal("fetch", fetchMock);

    const onApplyUpdates = vi.fn();
    render(<TestComponent onApplyUpdates={onApplyUpdates} />);

    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    await waitFor(() => {
      expect(screen.getByTestId("history-count")).toHaveTextContent("2");
    });

    expect(onApplyUpdates).toHaveBeenCalledWith([
      { action: "create_card", column_id: 1, title: "New AI task" },
    ]);
    expect(fetchMock).toHaveBeenCalled();
    expect(screen.getByText("assistant: Ok, I added a card.")).toBeInTheDocument();
  });

  it("persists history in localStorage", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({ response: "Hello" }),
    }));
    vi.stubGlobal("fetch", fetchMock);

    const onApplyUpdates = vi.fn();
    render(<TestComponent onApplyUpdates={onApplyUpdates} />);

    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    await waitFor(() => {
      expect(screen.getByTestId("history-count")).toHaveTextContent("2");
    });

    expect(localStorage.getItem("pm-ai-chat-history")).toContain("Hello");
    expect(fetchMock).toHaveBeenCalled();
  });
});
