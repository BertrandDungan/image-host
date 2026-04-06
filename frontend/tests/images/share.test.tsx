import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { SharePopover } from "../../images/share";
import { Api } from "../../api";
import { FetchError, ResponseError } from "../../api-client/runtime";

vi.mock("../../api", () => ({
  Api: {
    shareLinks: {
      shareLinksCreate: vi.fn(),
    },
  },
}));

describe("SharePopover", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders null when closed", () => {
    const { container } = render(
      <SharePopover originalImageId={9} open={false} onClose={vi.fn()} />,
    );
    expect(container.firstChild).toBeNull();
  });

  it("creates a share link successfully", async () => {
    vi.mocked(Api.shareLinks.shareLinksCreate).mockResolvedValue({
      id: 1,
      url: "https://host/share/abc",
      expiry: new Date("2026-01-01T00:00:00Z"),
      image: 9,
    });

    render(<SharePopover originalImageId={9} open onClose={vi.fn()} />);

    fireEvent.click(screen.getByRole("button", { name: "Create link" }));
    expect(
      await screen.findByText("https://host/share/abc"),
    ).toBeInTheDocument();
  });

  it("closes on escape", () => {
    const onClose = vi.fn();
    render(<SharePopover originalImageId={9} open onClose={onClose} />);

    fireEvent.keyDown(window, { key: "Escape" });
    expect(onClose).toHaveBeenCalled();
  });

  it("shows response error details", async () => {
    vi.mocked(Api.shareLinks.shareLinksCreate).mockRejectedValue(
      new ResponseError(
        new Response(JSON.stringify({ detail: "Invalid expiry" }), {
          status: 400,
        }),
      ),
    );

    render(<SharePopover originalImageId={9} open onClose={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "Create link" }));

    expect(await screen.findByText("Invalid expiry")).toBeInTheDocument();
  });

  it("shows network error message for FetchError", async () => {
    vi.mocked(Api.shareLinks.shareLinksCreate).mockRejectedValue(
      new FetchError(new Error("offline")),
    );

    render(<SharePopover originalImageId={9} open onClose={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "Create link" }));

    expect(
      await screen.findByText(
        "Network error. Check your connection and try again.",
      ),
    ).toBeInTheDocument();
  });
});
