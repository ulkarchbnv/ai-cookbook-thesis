import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import HomePage from "./pages/HomePage";
import GenerateRecipePage from "./pages/GenerateRecipePage";
import SavedRecipesPage from "./pages/SavedRecipesPage";
import LoginPage from "./pages/LoginPage";
import NutritionPage from "./pages/NutritionPage";

function App() {
  return (
    <BrowserRouter>
      <div>
        <nav>
          <Link to="/">Home</Link> |{" "}
          <Link to="/generate">Generate Recipe</Link> |{" "}
          <Link to="/nutrition">Nutrition Info</Link> |{" "}
          <Link to="/saved">Saved Recipes</Link> |{" "}
          <Link to="/login">Login</Link>
        </nav>

        <hr />

        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/generate" element={<GenerateRecipePage />} />
          <Route path="/nutrition" element={<NutritionPage />} />
          <Route path="/saved" element={<SavedRecipesPage />} />
          <Route path="/login" element={<LoginPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;