import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, test, vi } from "vitest";
import LoginPage from "./LoginPage";

const mockApiFetch = vi.fn();
const mockUseAuth = vi.fn();
const mockLogin = vi.fn();
const mockUpdateProfile = vi.fn();

vi.mock("../lib/api", () => ({
  apiFetch: (...args) => mockApiFetch(...args),
}));

vi.mock("../context/AuthContext", () => ({
  useAuth: () => mockUseAuth(),
}));

describe("LoginPage", () => {
  beforeEach(() => {
    mockApiFetch.mockReset();
    mockUseAuth.mockReset();
    mockLogin.mockReset();
    mockUpdateProfile.mockReset();
  });

  test("submits login credentials and stores the access token", async () => {
    mockUseAuth.mockReturnValue({
      token: null,
      profile: null,
      login: mockLogin,
      updateProfile: mockUpdateProfile,
    });
    mockApiFetch.mockResolvedValue({
      access_token: "token-123",
      token_type: "bearer",
    });

    render(<LoginPage />);

    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "tester@example.com" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "secret-password" },
    });
    fireEvent.click(screen.getAllByRole("button", { name: "Login" })[1]);

    expect(await screen.findByText("Login successful.")).toBeInTheDocument();
    expect(mockApiFetch).toHaveBeenCalledWith(
      "/login",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: "tester@example.com",
          password: "secret-password",
        }),
      })
    );
    expect(mockLogin).toHaveBeenCalledWith("token-123");
  });

  test("updates saved dietary defaults for authenticated users", async () => {
    mockUseAuth.mockReturnValue({
      token: "token-123",
      profile: {
        email: "tester@example.com",
        preferences: ["vegetarian"],
        allergies: ["peanut"],
      },
      login: mockLogin,
      updateProfile: mockUpdateProfile,
    });
    mockApiFetch.mockResolvedValue({
      email: "tester@example.com",
      preferences: ["vegan"],
      allergies: ["milk"],
    });

    render(<LoginPage />);

    fireEvent.change(screen.getByLabelText("Dietary Preferences"), {
      target: { value: "vegan" },
    });
    fireEvent.change(screen.getByLabelText("Allergies"), {
      target: { value: "milk" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Update Profile" }));

    expect(await screen.findByText("Profile updated successfully.")).toBeInTheDocument();
    expect(mockApiFetch).toHaveBeenCalledWith(
      "/me",
      expect.objectContaining({
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer token-123",
        },
        body: JSON.stringify({
          preferences: ["vegan"],
          allergies: ["milk"],
        }),
      })
    );
    expect(mockUpdateProfile).toHaveBeenCalledWith({
      email: "tester@example.com",
      preferences: ["vegan"],
      allergies: ["milk"],
    });
  });
});
