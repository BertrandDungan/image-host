import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import UploadForm from "../../images/uploadForm";
import { renderWithRouter } from "../utils/renderWithRouter";
import { Api } from "../../api";
import { AccountTierEnum } from "../../api-client/models/AccountTierEnum";
import { FetchError, ResponseError } from "../../api-client/runtime";

vi.mock("../../api", () => ({
  Api: {
    images: {
      imagesUpdate: vi.fn(),
    },
  },
}));

describe("UploadForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders message when no user is selected", () => {
    renderWithRouter(<UploadForm currentUser={null} />);
    expect(
      screen.getByText("Select a user on the home page to upload images."),
    ).toBeInTheDocument();
  });

  it("uploads a valid image and shows success", async () => {
    vi.mocked(Api.images.imagesUpdate).mockResolvedValue(undefined as never);
    renderWithRouter(
      <UploadForm
        currentUser={{ id: 2, name: "Bob", accountTier: AccountTierEnum.Basic }}
      />,
    );

    const fileInput = screen.getByLabelText("Image file (PNG or JPEG)");
    const submit = screen.getByRole("button", { name: "Upload" });

    expect(submit).toBeDisabled();
    fireEvent.change(fileInput, {
      target: { files: [new File(["img"], "a.png", { type: "image/png" })] },
    });

    expect(submit).toBeEnabled();
    fireEvent.click(submit);

    await waitFor(() =>
      expect(Api.images.imagesUpdate).toHaveBeenCalledWith({
        userId: 2,
        filename: "a.png",
        image: expect.any(File),
      }),
    );
    expect(
      await screen.findByText("Image uploaded successfully."),
    ).toBeInTheDocument();
  });

  it("shows file-type validation error", () => {
    renderWithRouter(
      <UploadForm
        currentUser={{ id: 2, name: "Bob", accountTier: AccountTierEnum.Basic }}
      />,
    );

    fireEvent.change(screen.getByLabelText("Image file (PNG or JPEG)"), {
      target: { files: [new File(["txt"], "a.txt", { type: "text/plain" })] },
    });

    expect(
      screen.getByText("Only PNG or JPEG files are allowed."),
    ).toBeInTheDocument();
  });

  it("shows response error details", async () => {
    vi.mocked(Api.images.imagesUpdate).mockRejectedValue(
      new ResponseError(
        new Response(JSON.stringify({ detail: "Too large" }), { status: 400 }),
      ),
    );
    renderWithRouter(
      <UploadForm
        currentUser={{ id: 2, name: "Bob", accountTier: AccountTierEnum.Basic }}
      />,
    );

    fireEvent.change(screen.getByLabelText("Image file (PNG or JPEG)"), {
      target: { files: [new File(["img"], "a.png", { type: "image/png" })] },
    });
    fireEvent.click(screen.getByRole("button", { name: "Upload" }));

    expect(await screen.findByText("Too large")).toBeInTheDocument();
  });

  it("shows fetch error message", async () => {
    vi.mocked(Api.images.imagesUpdate).mockRejectedValue(
      new FetchError(new Error("offline")),
    );
    renderWithRouter(
      <UploadForm
        currentUser={{ id: 2, name: "Bob", accountTier: AccountTierEnum.Basic }}
      />,
    );

    fireEvent.change(screen.getByLabelText("Image file (PNG or JPEG)"), {
      target: { files: [new File(["img"], "a.png", { type: "image/png" })] },
    });
    fireEvent.click(screen.getByRole("button", { name: "Upload" }));

    expect(
      await screen.findByText(
        "Network error. Check your connection and try again.",
      ),
    ).toBeInTheDocument();
  });
});
