import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { apiFetch } from "../lib/api";

function LoginPage() {
  const { token, profile, login, updateProfile } = useAuth();
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [preferences, setPreferences] = useState(
    () => profile?.preferences.join(", ") ?? ""
  );
  const [allergies, setAllergies] = useState(
    () => profile?.allergies.join(", ") ?? ""
  );

  useEffect(() => {
    if (profile) {
      setPreferences(profile.preferences.join(", "));
      setAllergies(profile.allergies.join(", "));
    }
  }, [profile]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    setError("");

    try {
      if (mode === "signup") {
        await apiFetch("/signup", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        setMessage("Account created. You can now log in.");
        setMode("login");
      } else {
        const data = await apiFetch("/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        login(data.access_token);
        setMessage("Login successful.");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleProfileUpdate = async (event) => {
    event.preventDefault();
    if (!token) return;

    setLoading(true);
    setMessage("");
    setError("");

    try {
      const data = await apiFetch("/me", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          preferences: preferences.split(",").map((item) => item.trim()).filter(Boolean),
          allergies: allergies.split(",").map((item) => item.trim()).filter(Boolean),
        }),
      });
      updateProfile(data);
      setMessage("Profile updated successfully.");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-card">
      <h1>{token ? "Account" : "Welcome"}</h1>
      <p className="page-subtitle">
        {token
          ? "Manage your dietary preferences and allergy defaults. These are applied automatically when generating recipes."
          : "Create an account or log in to save recipes, track your generation history, and store food label scans."}
      </p>

      {!token && (
        <>
          <div className="auth-tabs">
            <button
              type="button"
              onClick={() => { setMode("login"); setMessage(""); setError(""); }}
              className={`auth-tab${mode === "login" ? " active" : ""}`}
            >
              Login
            </button>
            <button
              type="button"
              onClick={() => { setMode("signup"); setMessage(""); setError(""); }}
              className={`auth-tab${mode === "signup" ? " active" : ""}`}
            >
              Sign Up
            </button>
          </div>

          <form onSubmit={handleSubmit} className="form-stack">
            <div className="field-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
              />
            </div>

            <div className="field-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            <button type="submit" disabled={loading}>
              {loading
                ? "Please wait..."
                : mode === "signup"
                ? "Create Account"
                : "Login"}
            </button>
          </form>
        </>
      )}

      {message && <p className="message success" style={{ marginTop: "0.75rem" }}>{message}</p>}
      {error && <p className="message error" style={{ marginTop: "0.75rem" }}>{error}</p>}

      {token && profile && (
        <>
          <div className="profile-summary">
            <div className="profile-summary-item">
              <div className="summary-label">Email</div>
              <div style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--color-text)" }}>{profile.email}</div>
            </div>
            <div className="profile-summary-item">
              <div className="summary-label">Preferences</div>
              <div className="tag-row" style={{ marginTop: "0.15rem" }}>
                {profile.preferences.length > 0
                  ? profile.preferences.map((item, index) => (
                      <span key={index} className="tag preference">{item}</span>
                    ))
                  : <span style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>None set</span>}
              </div>
            </div>
            <div className="profile-summary-item">
              <div className="summary-label">Allergies</div>
              <div className="tag-row" style={{ marginTop: "0.15rem" }}>
                {profile.allergies.length > 0
                  ? profile.allergies.map((item, index) => (
                      <span key={index} className="tag allergy">{item}</span>
                    ))
                  : <span style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>None set</span>}
              </div>
            </div>
          </div>

          <hr className="card-divider" />

          <h2>Update Defaults</h2>
          <p className="page-subtitle" style={{ marginBottom: "0.75rem" }}>
            These values auto-fill when you leave the preference or allergy fields empty on the Generate page.
          </p>

          <form onSubmit={handleProfileUpdate} className="form-stack">
            <div className="field-group">
              <label htmlFor="saved-preferences">Dietary Preferences</label>
              <input
                id="saved-preferences"
                type="text"
                value={preferences}
                onChange={(e) => setPreferences(e.target.value)}
                placeholder="e.g. halal, vegetarian"
              />
              <p className="field-hint">Separate with commas</p>
            </div>

            <div className="field-group">
              <label htmlFor="saved-allergies">Allergies</label>
              <input
                id="saved-allergies"
                type="text"
                value={allergies}
                onChange={(e) => setAllergies(e.target.value)}
                placeholder="e.g. peanut, milk"
              />
              <p className="field-hint">Separate with commas</p>
            </div>

            <button type="submit" disabled={loading}>
              {loading ? "Saving..." : "Update Profile"}
            </button>
          </form>
        </>
      )}
    </div>
  );
}

export default LoginPage;
