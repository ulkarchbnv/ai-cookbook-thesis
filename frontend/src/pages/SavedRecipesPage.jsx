import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiFetch, buildApiUrl } from "../lib/api";
import NutritionGrid from "../components/NutritionGrid";

const PAGE_SIZE = 10;

function SavedRecipesPage() {
  const { token } = useAuth();
  const [recipes, setRecipes] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadRecipes = async (targetPage = 1) => {
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const data = await apiFetch(`/recipes?page=${targetPage}&page_size=${PAGE_SIZE}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setRecipes(data.items);
      setTotal(data.total);
      setPage(data.page);
      setTotalPages(data.total_pages);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!token) { setRecipes([]); setTotal(0); return; }
    loadRecipes(1);
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
      <div className="history-header">
        <h1>Saved Recipes</h1>
        {total > 0 && (
          <span className="history-badge">
            {total} {total === 1 ? "recipe" : "recipes"}
          </span>
        )}
      </div>
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

      {totalPages > 1 && (
        <div className="pagination-bar">
          <button
            type="button"
            className="page-btn"
            disabled={page <= 1 || loading}
            onClick={() => loadRecipes(page - 1)}
          >
            ‹ Prev
          </button>
          <span className="page-info">
            Page {page} of {totalPages}
          </span>
          <button
            type="button"
            className="page-btn"
            disabled={page >= totalPages || loading}
            onClick={() => loadRecipes(page + 1)}
          >
            Next ›
          </button>
        </div>
      )}
    </div>
  );
}

export default SavedRecipesPage;
