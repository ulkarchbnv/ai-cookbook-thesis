import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, test, vi } from "vitest";
import RecipeHistoryPage from "./RecipeHistoryPage";

const mockApiFetch = vi.fn();
const mockUseAuth = vi.fn();

vi.mock("../lib/api", () => ({
  apiFetch: (...args) => mockApiFetch(...args),
  buildApiUrl: (path) => `http://127.0.0.1:8000${path}`,
}));

vi.mock("../context/AuthContext", () => ({
  useAuth: () => mockUseAuth(),
}));

describe("RecipeHistoryPage", () => {
  beforeEach(() => {
    mockApiFetch.mockReset();
    mockUseAuth.mockReset();
  });

  test("asks guests to log in before viewing recipe history", () => {
    mockUseAuth.mockReturnValue({ token: null });

    render(<RecipeHistoryPage />);

    expect(screen.getByRole("heading", { name: "Recipe History" })).toBeInTheDocument();
    expect(screen.getByText("Please log in to view your recipe history.")).toBeInTheDocument();
  });

  test("renders history entries and expands recipe details", async () => {
    mockUseAuth.mockReturnValue({ token: "token-123" });
    mockApiFetch.mockResolvedValue({
      items: [
        {
          id: 11,
          title: "Tomato Basil Pasta",
          ingredients: ["tomato", "basil", "pasta"],
          additional_ingredients: ["olive oil"],
          preferences: ["vegetarian"],
          allergies: ["peanut"],
          steps: ["Boil pasta", "Mix sauce"],
          nutrition: {
            calories: 420,
            protein: "18g",
            carbs: "54g",
            fat: "11g",
          },
          warnings: ["Used stored preferences."],
          image_url: null,
          image_cache_key: null,
          is_saved: true,
          saved_at: "2026-04-20T15:00:00Z",
          created_at: "2026-04-20T14:55:00Z",
        },
      ],
      total: 1,
      page: 1,
      page_size: 10,
      total_pages: 1,
    });

    render(<RecipeHistoryPage />);

    expect(await screen.findByText("Tomato Basil Pasta")).toBeInTheDocument();
    expect(screen.getByText("Saved")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Steps & nutrition" }));

    expect(screen.getByText("Preparation Steps")).toBeInTheDocument();
    expect(screen.getByText("Boil pasta")).toBeInTheDocument();
    expect(screen.getByText("Nutrition Estimate")).toBeInTheDocument();
  });
});
