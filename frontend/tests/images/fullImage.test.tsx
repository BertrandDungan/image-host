import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import FullImage from "../../images/fullImage";

describe("FullImage", () => {
  it("renders image with URL", () => {
    const { container } = render(
      <FullImage url="https://cdn/original-a.png" />,
    );
    expect(container.querySelector("img")).toHaveAttribute(
      "src",
      "https://cdn/original-a.png",
    );
  });

  it("updates image source on rerender", () => {
    const { container, rerender } = render(
      <FullImage url="https://cdn/original-a.png" />,
    );
    rerender(<FullImage url="https://cdn/original-b.png" />);
    expect(container.querySelector("img")).toHaveAttribute(
      "src",
      "https://cdn/original-b.png",
    );
  });
});
