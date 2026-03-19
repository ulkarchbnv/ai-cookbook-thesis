import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

function SavedRecipesPage({ token }) {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      setRecipes([]);
      return;
    }

    const loadRecipes = async () => {
      setLoading(true);
      setError("");

      try {
        const data = await apiFetch("/recipes", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setRecipes(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadRecipes();
  }, [token]);

  if (!token) {
    return (
      <div className="page-card">
        <h1>Saved Recipes</h1>
        <p>Please log in first to view your saved recipes.</p>
      </div>
    );
  }

  return (
    <div className="page-card">
      <h1>Saved Recipes</h1>
      <p className="section-copy">Browse the recipes you saved while testing and using the app.</p>

      {loading && <p>Loading saved recipes...</p>}
      {error && <p className="message error">{error}</p>}
      {!loading && !error && recipes.length === 0 && <p className="empty-state">No saved recipes yet.</p>}

      {recipes.map((recipe) => (
        <div key={recipe.id} className="recipe-card">
          <h2>{recipe.title}</h2>
          <p><strong>Ingredients:</strong> {recipe.ingredients.join(", ")}</p>
          <p><strong>Preferences:</strong> {recipe.preferences.join(", ") || "None"}</p>
          <p><strong>Allergies:</strong> {recipe.allergies.join(", ") || "None"}</p>

          <div className="result-block">
            <h3 className="section-title">Steps</h3>
            <ul className="result-list">
            {recipe.steps.map((step, index) => (
              <li key={`${recipe.id}-${index}`}>{step}</li>
            ))}
            </ul>
          </div>

          <p><strong>Calories:</strong> {recipe.nutrition.calories}</p>
          <p><strong>Protein:</strong> {recipe.nutrition.protein}</p>
          <p><strong>Carbs:</strong> {recipe.nutrition.carbs}</p>
          <p><strong>Fat:</strong> {recipe.nutrition.fat}</p>
        </div>
      ))}
    </div>
  );
}

export default SavedRecipesPage;
