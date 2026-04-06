import { fireEvent, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import Home from "../home";
import { renderWithRouter } from "./utils/renderWithRouter";
import { AccountTierEnum } from "../api-client/models/AccountTierEnum";

vi.mock("../users.tsx", () => ({
  UserDebugModal: ({ open }: { open: boolean }) =>
    open ? <div data-testid="user-debug-modal">Modal</div> : null,
}));

describe("Home", () => {
  it("renders logged-out state", () => {
    renderWithRouter(<Home currentUser={null} setCurrentUser={vi.fn()} />);

    expect(screen.getByText("Welcome to Image Host")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "View images" })).toBeDisabled();
    expect(
      screen.getByRole("button", { name: "Upload images" }),
    ).toBeDisabled();
  });

  it("renders logged-in state with links", () => {
    renderWithRouter(
      <Home
        currentUser={{
          id: 1,
          name: "Alice",
          accountTier: AccountTierEnum.Basic,
        }}
        setCurrentUser={vi.fn()}
      />,
    );

    expect(screen.getByText("Welcome Alice")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "View images" })).toHaveAttribute(
      "href",
      "/images",
    );
    expect(screen.getByRole("link", { name: "Upload images" })).toHaveAttribute(
      "href",
      "/image-upload",
    );
  });

  it("opens user debug modal when selecting a user", () => {
    renderWithRouter(<Home currentUser={null} setCurrentUser={vi.fn()} />);

    fireEvent.click(screen.getByRole("button", { name: "Select a user" }));
    expect(screen.getByTestId("user-debug-modal")).toBeInTheDocument();
  });
});
