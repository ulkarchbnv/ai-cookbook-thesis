import { useState } from "react";
import { apiFetch } from "../lib/api";

function LoginPage({ token, onAuthSuccess }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

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

  return (
    <div className="page-card">
      <h1>{token ? "Account" : "Login"}</h1>
      <p className="section-copy">
        {token ? "You are logged in and can save generated recipes." : "Create an account or log in to save recipes."}
      </p>

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

      {message && <p className="message">{message}</p>}
      {error && <p className="message error">{error}</p>}
    </div>
  );
}

export default LoginPage;
