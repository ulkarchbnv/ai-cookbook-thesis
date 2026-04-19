import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiFetch, buildApiUrl } from "../lib/api";
import NutritionGrid from "../components/NutritionGrid";

const PAGE_SIZE = 10;

function HistoryCard({ entry }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="recipe-card">
      <div className="recipe-hero">
        {entry.image_url && (
          <img
            src={buildApiUrl(entry.image_url)}
            alt={`Thumbnail for ${entry.title}`}
            className="recipe-image-preview"
          />
        )}
        <div>
          <div className="history-header">
            <h2>{entry.title}</h2>
            <span className={`history-badge${entry.is_saved ? " saved" : ""}`}>
              {entry.is_saved ? "Saved" : "Generated"}
            </span>
          </div>

          <p className="history-meta">
            {new Date(entry.created_at).toLocaleString()}
            {entry.saved_at && ` \u00B7 Saved ${new Date(entry.saved_at).toLocaleDateString()}`}
          </p>

          <p className="section-label">Ingredients</p>
          <div className="tag-row">
            {entry.ingredients
              .filter((item) => !(entry.additional_ingredients || []).includes(item))
              .map((item, index) => (
                <span key={index} className="tag">{item}</span>
              ))}
          </div>
          {entry.additional_ingredients?.length > 0 && (
            <div style={{ marginTop: "0.3rem" }}>
              <p className="section-label">You may also need</p>
              <div className="tag-row">
                {entry.additional_ingredients.map((item, index) => (
                  <span key={index} className="tag additional">{item}</span>
                ))}
              </div>
            </div>
          )}

          {entry.preferences?.length > 0 && (
            <div className="tag-row" style={{ marginTop: "0.25rem" }}>
              {entry.preferences.map((item, index) => (
                <span key={index} className="tag preference">{item}</span>
              ))}
            </div>
          )}

          {entry.allergies?.length > 0 && (
            <div className="tag-row" style={{ marginTop: "0.25rem" }}>
              {entry.allergies.map((item, index) => (
                <span key={index} className="tag allergy">{item}</span>
              ))}
            </div>
          )}

          {entry.warnings?.length > 0 && (
            <div style={{ marginTop: "0.35rem" }}>
              {entry.warnings.map((warning, index) => (
                <div key={`${entry.id}-w-${index}`} className="alert-box warning" style={{ marginBottom: "0.25rem" }}>
                  {warning}
                </div>
              ))}
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
              {entry.steps.map((step, index) => (
                <li key={`${entry.id}-${index}`}>{step}</li>
              ))}
            </ol>
          </div>

          <div className="result-block">
            <p className="section-title">Nutrition Estimate</p>
            <NutritionGrid nutrition={entry.nutrition} />
          </div>
        </>
      )}
    </div>
  );
}

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
        <p className="page-subtitle">Please log in to view your recipe history.</p>
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
      <p className="page-subtitle">
        Every recipe generated on your account, including those you didn't save.
        Click a card to expand full details.
      </p>

      {loading && <div className="loading-bar">Loading history...</div>}
      {error && <p className="message error">{error}</p>}
      {!loading && !error && historyEntries.length === 0 && (
        <div className="empty-state">
          <span className="empty-state-icon" aria-hidden="true">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
          </span>
          No generated recipes yet. Try generating one first.
        </div>
      )}

      {historyEntries.map((entry) => (
        <HistoryCard key={entry.id} entry={entry} />
      ))}

      {totalPages > 1 && (
        <div className="pagination-bar">
          <button
            type="button"
            className="page-btn"
            disabled={page <= 1 || loading}
            onClick={() => loadHistory(page - 1)}
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
            onClick={() => loadHistory(page + 1)}
          >
            Next &#8250;
          </button>
        </div>
      )}
    </div>
  );
}

export default RecipeHistoryPage;
