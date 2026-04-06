import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import ImageGridItem from "../../images/gridItem";

vi.mock("../../images/share", () => ({
  SharePopover: ({ open }: { open: boolean }) =>
    open ? <div data-testid="share-popover">Open</div> : null,
}));

describe("ImageGridItem", () => {
  const item = { id: 7, url: "https://cdn/7-200.png" };

  it("renders image thumbnail", () => {
    const { container } = render(
      <ImageGridItem
        item={item}
        thumbMax={200}
        originalUrl={undefined}
        shareEnabled={false}
        onViewFull={vi.fn()}
      />,
    );

    expect(container.querySelector("img")).toHaveAttribute("src", item.url);
  });

  it("calls onViewFull when original URL is available", () => {
    const onViewFull = vi.fn();
    render(
      <ImageGridItem
        item={item}
        thumbMax={200}
        originalUrl={"https://cdn/7-original.png"}
        shareEnabled={true}
        onViewFull={onViewFull}
      />,
    );

    fireEvent.click(
      screen.getByRole("button", { name: "View full-size image" }),
    );
    expect(onViewFull).toHaveBeenCalledWith("https://cdn/7-original.png");
  });

  it("toggles share popover when sharing is enabled", () => {
    render(
      <ImageGridItem
        item={item}
        thumbMax={200}
        originalUrl={undefined}
        shareEnabled={true}
        onViewFull={vi.fn()}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Share image" }));
    expect(screen.getByTestId("share-popover")).toBeInTheDocument();
  });

  it("keeps share disabled when enterprise sharing is unavailable", () => {
    render(
      <ImageGridItem
        item={item}
        thumbMax={200}
        originalUrl={undefined}
        shareEnabled={false}
        onViewFull={vi.fn()}
      />,
    );

    const button = screen.getByRole("button", {
      name: "Share (Enterprise only)",
    });
    expect(button).toBeDisabled();
    fireEvent.click(button);
    expect(screen.queryByTestId("share-popover")).not.toBeInTheDocument();
  });
});
