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
      <h1>{token ? "Account" : "Login"}</h1>
      <p className="section-copy">
        {token
          ? "You are logged in and can save generated recipes."
          : "Create an account or log in to save recipes and track your history."}
      </p>

      {!token && (
        <>
          <div className="button-row">
            <button
              type="button"
              onClick={() => { setMode("login"); setMessage(""); setError(""); }}
              disabled={mode === "login"}
              className={mode !== "login" ? "secondary" : ""}
            >
              Login
            </button>
            <button
              type="button"
              onClick={() => { setMode("signup"); setMessage(""); setError(""); }}
              disabled={mode === "signup"}
              className={mode !== "signup" ? "secondary" : ""}
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

      {message && <p className="message success">{message}</p>}
      {error && <p className="message error">{error}</p>}

      {token && profile && (
        <>
          <hr className="card-divider" />
          <h2>Saved Profile</h2>
          <p className="section-copy">
            These defaults are applied automatically when preference or allergy fields
            are left empty on the Generate Recipe page.
          </p>

          <div className="tag-row" style={{ marginBottom: "1rem" }}>
            {profile.preferences.length > 0
              ? profile.preferences.map((item, index) => (
                  <span key={index} className="tag">{item}</span>
                ))
              : <span className="empty-state">No preferences saved</span>}
            {profile.allergies.map((item, index) => (
              <span key={index} className="tag allergy">{item}</span>
            ))}
          </div>

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
