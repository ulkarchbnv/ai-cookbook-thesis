import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, test, vi } from "vitest";
import GenerateRecipePage from "./GenerateRecipePage";

const mockApiFetch = vi.fn();
const mockUseAuth = vi.fn();

vi.mock("../lib/api", () => ({
  apiFetch: (...args) => mockApiFetch(...args),
  buildApiUrl: (path) => `http://127.0.0.1:8000${path}`,
}));

vi.mock("../context/AuthContext", () => ({
  useAuth: () => mockUseAuth(),
}));

describe("GenerateRecipePage", () => {
  beforeEach(() => {
    mockApiFetch.mockReset();
    mockUseAuth.mockReset();
  });

  test("shows a validation error when no ingredients are provided", async () => {
    mockUseAuth.mockReturnValue({
      token: null,
      profile: null,
    });

    render(<GenerateRecipePage />);

    fireEvent.click(screen.getByRole("button", { name: "Generate Recipe" }));

    expect(await screen.findByText("Please enter at least one ingredient.")).toBeInTheDocument();
    expect(mockApiFetch).not.toHaveBeenCalled();
  });

  test("uses saved profile defaults when optional fields are left blank", async () => {
    mockUseAuth.mockReturnValue({
      token: "test-token",
      profile: {
        preferences: ["vegetarian"],
        allergies: ["peanut"],
      },
    });
    mockApiFetch.mockResolvedValue({
      generated_recipe_id: 7,
      title: "Tomato Basil Pasta",
      ingredients: ["tomato", "basil", "pasta"],
      additional_ingredients: [],
      preferences: ["vegetarian"],
      allergies: ["peanut"],
      steps: ["Boil pasta", "Mix sauce"],
      nutrition_estimate: {
        calories: 420,
        protein: "18g",
        carbs: "54g",
        fat: "11g",
      },
      image_url: null,
      image_cache_key: null,
      warnings: [],
    });

    render(<GenerateRecipePage />);

    fireEvent.change(screen.getByLabelText("Ingredients *"), {
      target: { value: "tomato, basil, pasta" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Generate Recipe" }));

    expect(await screen.findByText("Tomato Basil Pasta")).toBeInTheDocument();
    expect(mockApiFetch).toHaveBeenCalledWith(
      "/generate-recipe",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          "Content-Type": "application/json",
          Authorization: "Bearer test-token",
        }),
        body: JSON.stringify({
          ingredients: ["tomato", "basil", "pasta"],
          preferences: ["vegetarian"],
          allergies: ["peanut"],
        }),
      })
    );
  });
});
