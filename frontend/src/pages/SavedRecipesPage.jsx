import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiFetch, buildApiUrl } from "../lib/api";
import NutritionGrid from "../components/NutritionGrid";

const PAGE_SIZE = 10;

function RecipeCard({ recipe }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="recipe-card">
      <div className="recipe-hero">
        {recipe.image_url && (
          <img
            src={buildApiUrl(recipe.image_url)}
            alt={`Thumbnail for ${recipe.title}`}
            className="recipe-image-preview"
          />
        )}
        <div>
          <div className="history-header">
            <h2>{recipe.title}</h2>
            {recipe.saved_at && (
              <span className="history-badge saved">
                Saved {new Date(recipe.saved_at).toLocaleDateString()}
              </span>
            )}
          </div>

          <p className="section-label">Ingredients</p>
          <div className="tag-row">
            {recipe.ingredients
              .filter((item) => !(recipe.additional_ingredients || []).includes(item))
              .map((item, index) => (
                <span key={index} className="tag">{item}</span>
              ))}
          </div>
          {recipe.additional_ingredients?.length > 0 && (
            <div style={{ marginTop: "0.3rem" }}>
              <p className="section-label">You may also need</p>
              <div className="tag-row">
                {recipe.additional_ingredients.map((item, index) => (
                  <span key={index} className="tag additional">{item}</span>
                ))}
              </div>
            </div>
          )}

          {recipe.preferences?.length > 0 && (
            <div style={{ marginTop: "0.4rem" }}>
              <div className="tag-row">
                {recipe.preferences.map((item, index) => (
                  <span key={index} className="tag preference">{item}</span>
                ))}
              </div>
            </div>
          )}

          {recipe.allergies?.length > 0 && (
            <div style={{ marginTop: "0.3rem" }}>
              <div className="tag-row">
                {recipe.allergies.map((item, index) => (
                  <span key={index} className="tag allergy">{item}</span>
                ))}
              </div>
            </div>
          )}

          <button
            type="button"
            className="detail-toggle"
            onClick={() => setExpanded(!expanded)}
          >
            <span className={`toggle-arrow${expanded ? " open" : ""}`}>
            <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor"><polygon points="1,1 9,5 1,9"/></svg>
          </span>
            {expanded ? "Hide details" : "Steps & nutrition"}
          </button>
        </div>
      </div>

      {expanded && (
        <>
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
        </>
      )}
    </div>
  );
}

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
        <p className="page-subtitle">Please log in to view your saved recipes.</p>
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
      <p className="page-subtitle">
        Your bookmarked recipes. Click any card to expand preparation steps and nutrition details.
      </p>

      {loading && <div className="loading-bar">Loading recipes...</div>}
      {error && <p className="message error">{error}</p>}
      {!loading && !error && recipes.length === 0 && (
        <div className="empty-state">
          <span className="empty-state-icon" aria-hidden="true">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
          </span>
          No saved recipes yet. Generate a recipe and save it to see it here.
        </div>
      )}

      {recipes.map((recipe) => (
        <RecipeCard key={recipe.id} recipe={recipe} />
      ))}

      {totalPages > 1 && (
        <div className="pagination-bar">
          <button
            type="button"
            className="page-btn"
            disabled={page <= 1 || loading}
            onClick={() => loadRecipes(page - 1)}
          >
            &#8249; Prev
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
            Next &#8250;
          </button>
        </div>
      )}
    </div>
  );
}

export default SavedRecipesPage;
