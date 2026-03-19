import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { useState } from "react";
import HomePage from "./pages/HomePage";
import GenerateRecipePage from "./pages/GenerateRecipePage";
import SavedRecipesPage from "./pages/SavedRecipesPage";
import LoginPage from "./pages/LoginPage";
import NutritionPage from "./pages/NutritionPage";

function App() {
  const [token, setToken] = useState(() => localStorage.getItem("token"));

  const handleAuthSuccess = (nextToken) => {
    localStorage.setItem("token", nextToken);
    setToken(nextToken);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
  };

  return (
    <BrowserRouter>
      <div className="app-shell">
        <nav className="nav-bar">
          <Link to="/">Home</Link> |{" "}
          <Link to="/generate">Generate Recipe</Link> |{" "}
          <Link to="/nutrition">Nutrition Info</Link> |{" "}
          <Link to="/saved">Saved Recipes</Link> |{" "}
          <Link to="/login">{token ? "Account" : "Login"}</Link>
          {token && (
            <button type="button" onClick={handleLogout} className="link-button">
              Logout
            </button>
          )}
        </nav>

        <hr />

        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/generate" element={<GenerateRecipePage token={token} />} />
          <Route path="/nutrition" element={<NutritionPage />} />
          <Route path="/saved" element={<SavedRecipesPage token={token} />} />
          <Route path="/login" element={<LoginPage token={token} onAuthSuccess={handleAuthSuccess} />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
