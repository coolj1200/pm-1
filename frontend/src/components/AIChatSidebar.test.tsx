import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { AIChatSidebar } from "@/components/AIChatSidebar";

describe("AIChatSidebar", () => {
  it("calls onSend when a message is submitted", async () => {
    const onSend = vi.fn(() => Promise.resolve());
    const onClear = vi.fn();

    render(
      <AIChatSidebar
        history={[]}
        loading={false}
        error={null}
        onSend={onSend}
        onClear={onClear}
      />
    );

    const input = screen.getByLabelText("Chat message");
    await userEvent.type(input, "Add a task");
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(onSend).toHaveBeenCalledWith("Add a task");
  });

  it("clears history when the button is clicked", async () => {
    const onSend = vi.fn(() => Promise.resolve());
    const onClear = vi.fn();

    render(
      <AIChatSidebar
        history={[]}
        loading={false}
        error={null}
        onSend={onSend}
        onClear={onClear}
      />
    );

    await userEvent.click(screen.getByRole("button", { name: /clear conversation/i }));

    expect(onClear).toHaveBeenCalled();
  });
});
