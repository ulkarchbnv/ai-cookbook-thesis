import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import { useState } from "react";
import "./App.css";
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
        <header className="site-header">
          <div className="brand-block">
            <p className="brand-kicker">AI Cookbook</p>
            <p className="brand-copy">Ingredient-based recipes, nutrition extraction, and saved cooking workflows.</p>
          </div>

          <nav className="nav-bar">
            <NavLink to="/" end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
              Home
            </NavLink>
            <NavLink to="/generate" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
              Generate Recipe
            </NavLink>
            <NavLink to="/nutrition" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
              Nutrition Info
            </NavLink>
            <NavLink to="/saved" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
              Saved Recipes
            </NavLink>
            <NavLink to="/login" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
              {token ? "Account" : "Login"}
            </NavLink>
            {token && (
              <button type="button" onClick={handleLogout} className="logout-button">
                Logout
              </button>
            )}
          </nav>
        </header>

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
