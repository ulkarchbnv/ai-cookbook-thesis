import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiFetch, buildApiUrl } from "../lib/api";
import NutritionGrid from "../components/NutritionGrid";

const PAGE_SIZE = 10;

function RecipeHistoryPage() {
  const { token } = useAuth();
  const [historyEntries, setHistoryEntries] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadHistory = async (targetPage = 1) => {
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const data = await apiFetch(`/recipes/history?page=${targetPage}&page_size=${PAGE_SIZE}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setHistoryEntries(data.items);
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
    if (!token) { setHistoryEntries([]); setTotal(0); return; }
    loadHistory(1);
  }, [token]);

  if (!token) {
    return (
      <div className="page-card">
        <h1>Recipe History</h1>
        <p className="section-copy">Please log in to view your recipe history.</p>
      </div>
    );
  }

  return (
    <div className="page-card">
      <div className="history-header">
        <h1>Recipe History</h1>
        {total > 0 && (
          <span className="history-badge">
            {total} {total === 1 ? "recipe" : "recipes"}
          </span>
        )}
      </div>
      <p className="section-copy">
        All generated recipes for your account, including those that were not saved.
      </p>

      {loading && <p className="section-copy">Loading...</p>}
      {error && <p className="message error">{error}</p>}
      {!loading && !error && historyEntries.length === 0 && (
        <p className="empty-state">No generated recipe history yet.</p>
      )}

      {historyEntries.map((entry) => (
        <div key={entry.id} className="recipe-card">
          <div className="history-header">
            <h2>{entry.title}</h2>
            <span className={`history-badge${entry.is_saved ? " saved" : ""}`}>
              {entry.is_saved ? "Saved" : "Generated"}
            </span>
          </div>

          {entry.image_url && (
            <img
              src={buildApiUrl(entry.image_url)}
              alt={`Thumbnail for ${entry.title}`}
              className="recipe-image-preview"
            />
          )}

          <p style={{ fontSize: "0.85rem", color: "#7a92a8", margin: "0 0 0.75rem" }}>
            {new Date(entry.created_at).toLocaleString()}
            {entry.saved_at && ` · Saved ${new Date(entry.saved_at).toLocaleDateString()}`}
          </p>

          <p className="section-title">Ingredients</p>
          <div className="tag-row">
            {entry.ingredients.map((item, index) => (
              <span key={index} className="tag">{item}</span>
            ))}
          </div>

          {entry.preferences?.length > 0 && (
            <>
              <p className="section-title" style={{ marginTop: "0.75rem" }}>Dietary Preferences</p>
              <div className="tag-row">
                {entry.preferences.map((item, index) => (
                  <span key={index} className="tag">{item}</span>
                ))}
              </div>
            </>
          )}

          {entry.allergies?.length > 0 && (
            <>
              <p className="section-title" style={{ marginTop: "0.75rem" }}>Allergies</p>
              <div className="tag-row">
                {entry.allergies.map((item, index) => (
                  <span key={index} className="tag allergy">{item}</span>
                ))}
              </div>
            </>
          )}

          {entry.warnings?.length > 0 && (
            <div style={{ margin: "0.5rem 0" }}>
              {entry.warnings.map((warning, index) => (
                <p key={`${entry.id}-w-${index}`} className="message error">{warning}</p>
              ))}
            </div>
          )}

          <div className="result-block">
            <p className="section-title">Preparation Steps</p>
            <ol className="result-list">
              {entry.steps.map((step, index) => (
                <li key={`${entry.id}-${index}`}>{step}</li>
              ))}
            </ol>
          </div>

          <div className="result-block">
            <p className="section-title">Nutrition Estimate</p>
            <NutritionGrid nutrition={entry.nutrition} />
          </div>
        </div>
      ))}

      {totalPages > 1 && (
        <div className="pagination-bar">
          <button
            type="button"
            className="page-btn"
            disabled={page <= 1 || loading}
            onClick={() => loadHistory(page - 1)}
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
            onClick={() => loadHistory(page + 1)}
          >
            Next ›
          </button>
        </div>
      )}
    </div>
  );
}

export default RecipeHistoryPage;
