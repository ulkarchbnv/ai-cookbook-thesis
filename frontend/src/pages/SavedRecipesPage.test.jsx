import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, test, vi } from "vitest";
import SavedRecipesPage from "./SavedRecipesPage";

const mockUseAuth = vi.fn();

vi.mock("../context/AuthContext", () => ({
  useAuth: () => mockUseAuth(),
}));

vi.mock("../lib/api", () => ({
  apiFetch: vi.fn(),
  buildApiUrl: (path) => `http://127.0.0.1:8000${path}`,
}));

describe("SavedRecipesPage", () => {
  beforeEach(() => {
    mockUseAuth.mockReset();
  });

  test("asks unauthenticated users to log in before viewing saved recipes", () => {
    mockUseAuth.mockReturnValue({
      token: null,
    });

    render(<SavedRecipesPage />);

    expect(screen.getByRole("heading", { name: "Saved Recipes" })).toBeInTheDocument();
    expect(screen.getByText("Please log in to view your saved recipes.")).toBeInTheDocument();
  });
});
