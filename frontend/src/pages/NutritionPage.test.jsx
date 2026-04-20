import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, test, vi } from "vitest";
import NutritionPage from "./NutritionPage";

const mockApiFetch = vi.fn();
const mockUseAuth = vi.fn();

vi.mock("../lib/api", () => ({
  apiFetch: (...args) => mockApiFetch(...args),
  buildApiUrl: (path) => `http://127.0.0.1:8000${path}`,
}));

vi.mock("../context/AuthContext", () => ({
  useAuth: () => mockUseAuth(),
}));

describe("NutritionPage", () => {
  beforeEach(() => {
    mockApiFetch.mockReset();
    mockUseAuth.mockReset();
    vi.stubGlobal("URL", {
      createObjectURL: vi.fn(() => "blob:preview"),
      revokeObjectURL: vi.fn(),
    });
  });

  test("shows an OCR validation error when submitted without a file", async () => {
    mockUseAuth.mockReturnValue({ token: null });

    const { container } = render(<NutritionPage />);
    fireEvent.submit(container.querySelector("form"));

    expect(await screen.findByText("Please choose a nutrition label image first.")).toBeInTheDocument();
    expect(mockApiFetch).not.toHaveBeenCalled();
  });

  test("loads saved OCR history for authenticated users and shows empty state", async () => {
    mockUseAuth.mockReturnValue({ token: "token-123" });
    mockApiFetch.mockResolvedValueOnce({
      items: [],
      total: 0,
      page: 1,
      page_size: 10,
      total_pages: 1,
    });

    render(<NutritionPage />);

    expect(await screen.findByText("Saved Food Labels")).toBeInTheDocument();
    expect(screen.getByText("No saved food labels yet. Extract a label above and save it.")).toBeInTheDocument();
  });

  test("renders extracted OCR nutrition after a valid file upload", async () => {
    mockUseAuth.mockReturnValue({ token: null });
    mockApiFetch.mockResolvedValue({
      raw_text: "Calories 180 Protein 12g",
      structured_nutrition: {
        product_name: "Protein Bar",
        serving_size: "1 bar",
        calories: 180,
        protein_g: 12,
        carbs_g: 15,
        fat_g: 7,
        sugar_g: 5,
        sodium_mg: 120,
        fiber_g: 3,
      },
      image_url: "/media/ocr_uploads/mock.png",
      image_path: "backend/media/ocr_uploads/mock.png",
    });

    const { container } = render(<NutritionPage />);
    const fileInput = container.querySelector('input[type="file"]');
    const file = new File(["fake-image"], "label.png", { type: "image/png" });

    fireEvent.change(fileInput, { target: { files: [file] } });
    fireEvent.submit(container.querySelector("form"));

    expect(await screen.findByText("Extracted Nutrition")).toBeInTheDocument();
    expect(screen.getByText("Protein Bar")).toBeInTheDocument();
    expect(screen.getByText(/1 bar per serving/)).toBeInTheDocument();
    expect(screen.getByText("Raw OCR Text")).toBeInTheDocument();
    expect(screen.getByText("Calories 180 Protein 12g")).toBeInTheDocument();

    await waitFor(() => {
      expect(mockApiFetch).toHaveBeenCalledWith(
        "/ocr/extract",
        expect.objectContaining({
          method: "POST",
          body: expect.any(FormData),
        })
      );
    });
  });
});
