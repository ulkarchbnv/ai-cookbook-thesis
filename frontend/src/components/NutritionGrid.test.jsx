import { render, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";
import NutritionGrid from "./NutritionGrid";

describe("NutritionGrid", () => {
  test("renders default nutrition fields for recipe output", () => {
    render(
      <NutritionGrid
        nutrition={{
          calories: 420,
          protein: "18g",
          carbs: "54g",
          fat: "11g",
        }}
      />
    );

    expect(screen.getByText("Calories")).toBeInTheDocument();
    expect(screen.getByText("420")).toBeInTheDocument();
    expect(screen.getByText("Protein")).toBeInTheDocument();
    expect(screen.getByText("18g")).toBeInTheDocument();
    expect(screen.getByText("Carbs")).toBeInTheDocument();
    expect(screen.getByText("54g")).toBeInTheDocument();
    expect(screen.getByText("Fat")).toBeInTheDocument();
    expect(screen.getByText("11g")).toBeInTheDocument();
  });

  test("renders custom OCR fields and shows a fallback for missing values", () => {
    render(
      <NutritionGrid
        nutrition={{}}
        fields={[
          { label: "Calories", value: 120 },
          { label: "Fiber (g)", value: null },
        ]}
      />
    );

    expect(screen.getByText("Calories")).toBeInTheDocument();
    expect(screen.getByText("120")).toBeInTheDocument();
    expect(screen.getByText("Fiber (g)")).toBeInTheDocument();
    expect(screen.getByText("—")).toBeInTheDocument();
  });
});
