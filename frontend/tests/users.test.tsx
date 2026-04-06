import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { UserDebugModal } from "../users";
import { Api } from "../api";
import { AccountTierEnum } from "../api-client/models/AccountTierEnum";

vi.mock("../api", () => ({
  Api: {
    users: {
      usersList: vi.fn(),
    },
  },
}));

describe("UserDebugModal", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("returns null when closed", () => {
    const { container } = render(
      <UserDebugModal
        open={false}
        onClose={vi.fn()}
        setCurrentUser={vi.fn()}
      />,
    );
    expect(container.firstChild).toBeNull();
  });

  it("loads users and sets current user", async () => {
    const onClose = vi.fn();
    const setCurrentUser = vi.fn();
    vi.mocked(Api.users.usersList).mockResolvedValue([
      { id: 1, name: "Alice", accountTier: AccountTierEnum.Basic },
    ]);

    render(
      <UserDebugModal open onClose={onClose} setCurrentUser={setCurrentUser} />,
    );

    expect(screen.getByText("Loading users…")).toBeInTheDocument();
    expect(await screen.findByText("Alice")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Set user" }));
    expect(setCurrentUser).toHaveBeenCalledWith({
      id: 1,
      name: "Alice",
      accountTier: AccountTierEnum.Basic,
    });
    expect(onClose).toHaveBeenCalled();
  });

  it("shows error when user loading fails", async () => {
    vi.mocked(Api.users.usersList).mockRejectedValue(new Error("nope"));

    render(<UserDebugModal open onClose={vi.fn()} setCurrentUser={vi.fn()} />);

    await waitFor(() =>
      expect(screen.getByText("Could not load users")).toBeInTheDocument(),
    );
  });
});
