import { useEffect, useState } from "react";
import { apiFetch, buildApiUrl } from "../lib/api";

function RecipeHistoryPage({ token }) {
  const [historyEntries, setHistoryEntries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      setHistoryEntries([]);
      return;
    }

    const loadHistory = async () => {
      setLoading(true);
      setError("");

      try {
        const data = await apiFetch("/recipes/history", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setHistoryEntries(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadHistory();
  }, [token]);

  if (!token) {
    return (
      <div className="page-card">
        <h1>Recipe History</h1>
        <p>Please log in first to view your generated recipe history.</p>
      </div>
    );
  }

  return (
    <div className="page-card">
      <h1>Recipe History</h1>
      <p className="section-copy">
        This page shows all generated recipes for your account, including recipes that were not saved.
      </p>

      {loading && <p>Loading recipe history...</p>}
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
              alt={`History thumbnail for ${entry.title}`}
              className="recipe-image-preview"
            />
          )}

          <p><strong>Generated:</strong> {new Date(entry.created_at).toLocaleString()}</p>
          {entry.saved_at && <p><strong>Saved:</strong> {new Date(entry.saved_at).toLocaleString()}</p>}
          <p><strong>Ingredients:</strong> {entry.ingredients.join(", ")}</p>
          <p><strong>Preferences:</strong> {entry.preferences.join(", ") || "None"}</p>
          <p><strong>Allergies:</strong> {entry.allergies.join(", ") || "None"}</p>

          {entry.warnings?.map((warning, index) => (
            <p key={`${entry.id}-warning-${index}`} className="message">
              {warning}
            </p>
          ))}

          <div className="result-block">
            <h3 className="section-title">Steps</h3>
            <ul className="result-list">
              {entry.steps.map((step, index) => (
                <li key={`${entry.id}-${index}`}>{step}</li>
              ))}
            </ul>
          </div>

          <p><strong>Calories:</strong> {entry.nutrition.calories}</p>
          <p><strong>Protein:</strong> {entry.nutrition.protein}</p>
          <p><strong>Carbs:</strong> {entry.nutrition.carbs}</p>
          <p><strong>Fat:</strong> {entry.nutrition.fat}</p>
        </div>
      ))}
    </div>
  );
}

export default RecipeHistoryPage;
