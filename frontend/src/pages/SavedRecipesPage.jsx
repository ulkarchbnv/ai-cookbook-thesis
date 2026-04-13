import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiFetch, buildApiUrl } from "../lib/api";
import NutritionGrid from "../components/NutritionGrid";

function SavedRecipesPage() {
  const { token } = useAuth();
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) { setRecipes([]); return; }
    const load = async () => {
      setLoading(true);
      setError("");
      try {
        const data = await apiFetch("/recipes", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setRecipes(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [token]);

  if (!token) {
    return (
      <div className="page-card">
        <h1>Saved Recipes</h1>
        <p className="section-copy">Please log in to view your saved recipes.</p>
      </div>
    );
  }

  return (
    <div className="page-card">
      <h1>Saved Recipes</h1>
      <p className="section-copy">Recipes you saved while using the app.</p>

      {loading && <p className="section-copy">Loading...</p>}
      {error && <p className="message error">{error}</p>}
      {!loading && !error && recipes.length === 0 && (
        <p className="empty-state">No saved recipes yet.</p>
      )}

      {recipes.map((recipe) => (
        <div key={recipe.id} className="recipe-card">
          <div className="history-header">
            <h2>{recipe.title}</h2>
            {recipe.saved_at && (
              <span className="history-badge saved">
                Saved {new Date(recipe.saved_at).toLocaleDateString()}
              </span>
            )}
          </div>

          {recipe.image_url && (
            <img
              src={buildApiUrl(recipe.image_url)}
              alt={`Thumbnail for ${recipe.title}`}
              className="recipe-image-preview"
            />
          )}

          <p className="section-title">Ingredients</p>
          <div className="tag-row">
            {recipe.ingredients.map((item, index) => (
              <span key={index} className="tag">{item}</span>
            ))}
          </div>

          {recipe.preferences?.length > 0 && (
            <>
              <p className="section-title" style={{ marginTop: "0.75rem" }}>Dietary Preferences</p>
              <div className="tag-row">
                {recipe.preferences.map((item, index) => (
                  <span key={index} className="tag">{item}</span>
                ))}
              </div>
            </>
          )}

          {recipe.allergies?.length > 0 && (
            <>
              <p className="section-title" style={{ marginTop: "0.75rem" }}>Allergies</p>
              <div className="tag-row">
                {recipe.allergies.map((item, index) => (
                  <span key={index} className="tag allergy">{item}</span>
                ))}
              </div>
            </>
          )}

          <div className="result-block">
            <p className="section-title">Preparation Steps</p>
            <ol className="result-list">
              {recipe.steps.map((step, index) => (
                <li key={`${recipe.id}-${index}`}>{step}</li>
              ))}
            </ol>
          </div>

          <div className="result-block">
            <p className="section-title">Nutrition Estimate</p>
            <NutritionGrid nutrition={recipe.nutrition} />
          </div>
        </div>
      ))}
    </div>
  );
}

export default SavedRecipesPage;
