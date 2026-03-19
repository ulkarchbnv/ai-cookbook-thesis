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

      {loading && <p>Loading saved recipes...</p>}
      {error && <p className="message error">{error}</p>}
      {!loading && !error && recipes.length === 0 && <p>No saved recipes yet.</p>}

      {recipes.map((recipe) => (
        <div key={recipe.id} className="recipe-card">
          <h2>{recipe.title}</h2>
          <p><strong>Ingredients:</strong> {recipe.ingredients.join(", ")}</p>
          <p><strong>Preferences:</strong> {recipe.preferences.join(", ") || "None"}</p>
          <p><strong>Allergies:</strong> {recipe.allergies.join(", ") || "None"}</p>
          <h3>Steps</h3>
          <ul>
            {recipe.steps.map((step, index) => (
              <li key={`${recipe.id}-${index}`}>{step}</li>
            ))}
          </ul>
          <h3>Nutrition</h3>
          <p>Calories: {recipe.nutrition.calories}</p>
          <p>Protein: {recipe.nutrition.protein}</p>
          <p>Carbs: {recipe.nutrition.carbs}</p>
          <p>Fat: {recipe.nutrition.fat}</p>
        </div>
      ))}
    </div>
  );
}

export default SavedRecipesPage;
