import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

function LoginPage({ token, profile, setProfile, onAuthSuccess }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [preferences, setPreferences] = useState("");
  const [allergies, setAllergies] = useState("");

  useEffect(() => {
    if (!token) {
      setProfile(null);
      return;
    }

    if (profile) {
      return;
    }

    const loadProfile = async () => {
      try {
        const data = await apiFetch("/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setProfile(data);
        setPreferences(data.preferences.join(", "));
        setAllergies(data.allergies.join(", "));
      } catch {
        localStorage.removeItem("token");
        onAuthSuccess(null);
      }
    };

    loadProfile();
  }, [token, profile, setProfile, onAuthSuccess]);

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
        onAuthSuccess(data.access_token);
        setMessage("Login successful.");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = async (event) => {
    event.preventDefault();
    if (!token) {
      return;
    }

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
      setProfile(data);
      setMessage("Profile updated.");
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
        {token ? "You are logged in and can save generated recipes." : "Create an account or log in to save recipes."}
      </p>

      {!token && (
        <>
          <div className="button-row">
            <button type="button" onClick={() => setMode("login")} disabled={mode === "login"}>
              Login
            </button>
            <button type="button" onClick={() => setMode("signup")} disabled={mode === "signup"}>
              Sign Up
            </button>
          </div>

          <form onSubmit={handleSubmit} className="form-stack">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />

            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />

            <button type="submit" disabled={loading}>
              {loading ? "Please wait..." : mode === "signup" ? "Create Account" : "Login"}
            </button>
          </form>
        </>
      )}

      {message && <p className="message">{message}</p>}
      {error && <p className="message error">{error}</p>}

      {token && (
        <form onSubmit={updateProfile} className="form-stack">
          <h2>Saved Preferences</h2>

          <label htmlFor="saved-preferences">Dietary Preferences</label>
          <input
            id="saved-preferences"
            type="text"
            value={preferences}
            onChange={(event) => setPreferences(event.target.value)}
            placeholder="e.g. halal, vegetarian"
          />

          <label htmlFor="saved-allergies">Allergies</label>
          <input
            id="saved-allergies"
            type="text"
            value={allergies}
            onChange={(event) => setAllergies(event.target.value)}
            placeholder="e.g. peanut, milk"
          />

          <button type="submit" disabled={loading}>
            {loading ? "Saving..." : "Save Profile"}
          </button>

          {profile && (
            <p className="section-copy">
              Stored preferences: {profile.preferences.join(", ") || "None"} | Stored allergies:{" "}
              {profile.allergies.join(", ") || "None"}
            </p>
          )}
        </form>
      )}
    </div>
  );
}

export default LoginPage;
