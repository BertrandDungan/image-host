import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import GridView from "../../images/gridView";
import { renderWithRouter } from "../utils/renderWithRouter";
import { Api } from "../../api";
import { AccountTierEnum } from "../../api-client/models/AccountTierEnum";

vi.mock("../../api", () => ({
  Api: {
    images: {
      imagesRetrieve: vi.fn(),
    },
  },
}));

describe("GridView", () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it("renders message when no user is selected", () => {
    renderWithRouter(<GridView currentUser={null} />);
    expect(
      screen.getByText("Select a user to view their images."),
    ).toBeInTheDocument();
  });

  it("loads and renders images for selected user", async () => {
    vi.mocked(Api.images.imagesRetrieve).mockResolvedValue({
      items: [{ id: 10, url: "testURL1" }],
    });

    const { container } = renderWithRouter(
      <GridView
        currentUser={{ id: 1, name: "Alice", accountTier: AccountTierEnum.Basic }}
      />,
    );

    await waitFor(() =>
      expect(container.querySelector("img")).toHaveAttribute(
        "src",
        "testURL1",
      ),
    );
    expect(container.querySelector("img")).toHaveAttribute(
      "src",
      "testURL1",
    );
    expect(Api.images.imagesRetrieve).toHaveBeenCalledWith({
      imageSize: "200",
      userId: 1,
    });
  });

  it("toggles thumbnail size for premium users", async () => {
    vi.mocked(Api.images.imagesRetrieve)
      .mockResolvedValueOnce({
        items: [{ id: 10, url: "testURL1" }],
      })
      .mockResolvedValueOnce({
        items: [{ id: 10, url: "testURL2" }],
      })
      .mockResolvedValueOnce({
        items: [{ id: 10, url: "testURL3" }],
      });

    const { container } = renderWithRouter(
      <GridView
        currentUser={{
          id: 1,
          name: "Alice",
          accountTier: AccountTierEnum.Premium,
        }}
      />,
    );
    await waitFor(() => expect(container.querySelector("img")).not.toBeNull());

    fireEvent.click(
      screen.getByRole("button", { name: "Switch to medium thumbnails" }),
    );

    await waitFor(() =>
      expect(Api.images.imagesRetrieve).toHaveBeenCalledWith({
        imageSize: "400",
        userId: 1,
      }),
    );
  });

  it("shows error when image loading fails", async () => {
    vi.mocked(Api.images.imagesRetrieve).mockRejectedValue(new Error("fail"));
    renderWithRouter(
      <GridView
        currentUser={{ id: 1, name: "Alice", accountTier: AccountTierEnum.Basic }}
      />,
    );

    expect(await screen.findByText("Could not load images")).toBeInTheDocument();
  });
});
