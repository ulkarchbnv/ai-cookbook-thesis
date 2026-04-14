import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import "./App.css";
import HomePage from "./pages/HomePage";
import GenerateRecipePage from "./pages/GenerateRecipePage";
import SavedRecipesPage from "./pages/SavedRecipesPage";
import LoginPage from "./pages/LoginPage";
import NutritionPage from "./pages/NutritionPage";
import RecipeHistoryPage from "./pages/RecipeHistoryPage";

function NavBar() {
  const { token, logout } = useAuth();

  return (
    <nav className="nav-bar">
      <NavLink to="/" end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
        Home
      </NavLink>
      <NavLink to="/generate" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
        Generate
      </NavLink>
      <NavLink to="/nutrition" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
        Food Labels
      </NavLink>
      <NavLink to="/saved" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
        Saved
      </NavLink>
      <NavLink to="/history" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
        History
      </NavLink>

      <span className="nav-spacer" />

      <NavLink to="/login" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
        {token ? "Account" : "Login"}
      </NavLink>
      {token && (
        <button type="button" onClick={logout} className="logout-button">
          Logout
        </button>
      )}
    </nav>
  );
}

function AppShell() {
  return (
    <div className="app-shell">
      <header className="site-header">
        <div className="brand-row">
          <span className="brand-logo" aria-hidden="true">&#x1F373;</span>
          <div>
            <p className="brand-name">AI Cookbook</p>
            <p className="brand-tagline">Ingredient-based recipes, nutrition extraction, and saved cooking workflows.</p>
          </div>
        </div>
        <NavBar />
      </header>

      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/generate" element={<GenerateRecipePage />} />
          <Route path="/nutrition" element={<NutritionPage />} />
          <Route path="/saved" element={<SavedRecipesPage />} />
          <Route path="/history" element={<RecipeHistoryPage />} />
          <Route path="/login" element={<LoginPage />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppShell />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
