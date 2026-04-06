import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import type { ReactElement } from "react";

/**
 * Test wrapper for components which have Router links.
 */
export function renderWithRouter(ui: ReactElement, route: string = "/") {
  return render(<MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>);
}
