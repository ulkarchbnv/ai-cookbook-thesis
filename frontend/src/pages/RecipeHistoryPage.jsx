import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiFetch, buildApiUrl } from "../lib/api";

function NutritionGrid({ nutrition }) {
  const fields = [
    { label: "Calories", value: nutrition.calories },
    { label: "Protein", value: nutrition.protein },
    { label: "Carbs", value: nutrition.carbs },
    { label: "Fat", value: nutrition.fat },
  ];
  return (
    <div className="nutrition-grid">
      {fields.map(({ label, value }) => (
        <div key={label} className="nutrition-cell">
          <div className="cell-label">{label}</div>
          <div className="cell-value">{value}</div>
        </div>
      ))}
    </div>
  );
}

function RecipeHistoryPage() {
  const { token } = useAuth();
  const [historyEntries, setHistoryEntries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) { setHistoryEntries([]); return; }
    const load = async () => {
      setLoading(true);
      setError("");
      try {
        const data = await apiFetch("/recipes/history", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setHistoryEntries(data);
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
        <h1>Recipe History</h1>
        <p className="section-copy">Please log in to view your recipe history.</p>
      </div>
    );
  }

  return (
    <div className="page-card">
      <h1>Recipe History</h1>
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

          <div className="tag-row">
            {entry.ingredients.map((item) => (
              <span key={item} className="tag">{item}</span>
            ))}
          </div>

          {entry.preferences?.length > 0 && (
            <div className="tag-row" style={{ marginTop: "0.35rem" }}>
              {entry.preferences.map((item) => (
                <span key={item} className="tag">{item}</span>
              ))}
            </div>
          )}

          {entry.allergies?.length > 0 && (
            <div className="tag-row" style={{ marginTop: "0.35rem" }}>
              {entry.allergies.map((item) => (
                <span key={item} className="tag allergy">{item}</span>
              ))}
            </div>
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
    </div>
  );
}

export default RecipeHistoryPage;