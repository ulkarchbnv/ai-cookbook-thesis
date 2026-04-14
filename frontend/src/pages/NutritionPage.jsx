import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiFetch, buildApiUrl } from "../lib/api";
import NutritionGrid from "../components/NutritionGrid";

const PAGE_SIZE = 10;

function NutritionPage() {
  const { token } = useAuth();
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [historyTotal, setHistoryTotal] = useState(0);
  const [historyPage, setHistoryPage] = useState(1);
  const [historyTotalPages, setHistoryTotalPages] = useState(1);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [saveLoading, setSaveLoading] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");
  const [isSaved, setIsSaved] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState("");

  const ocrNutritionFields = (nutrition) => [
    { label: "Calories", value: nutrition.calories },
    { label: "Protein (g)", value: nutrition.protein_g },
    { label: "Carbs (g)", value: nutrition.carbs_g },
    { label: "Fat (g)", value: nutrition.fat_g },
    { label: "Sugar (g)", value: nutrition.sugar_g },
    { label: "Sodium (mg)", value: nutrition.sodium_mg },
    { label: "Fiber (g)", value: nutrition.fiber_g },
  ];

  const loadHistory = async (page = 1) => {
    if (!token) return;
    setHistoryLoading(true);
    setHistoryError("");
    try {
      const data = await apiFetch(`/ocr/history?page=${page}&page_size=${PAGE_SIZE}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setHistory(data.items);
      setHistoryTotal(data.total);
      setHistoryPage(data.page);
      setHistoryTotalPages(data.total_pages);
    } catch (err) {
      setHistoryError(err.message);
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    if (!token) {
      setHistory([]);
      setHistoryError("");
      setHistoryTotal(0);
      setHistoryPage(1);
      return;
    }
    loadHistory(1);
  }, [token]);

  useEffect(() => {
    if (!selectedFile) {
      setImagePreviewUrl("");
      return undefined;
    }
    const url = URL.createObjectURL(selectedFile);
    setImagePreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [selectedFile]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setResult(null);
    setSaveMessage("");
    setIsSaved(false);

    if (!selectedFile) {
      setError("Please choose a nutrition label image first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);
    setLoading(true);

    try {
      const data = await apiFetch("/ocr/extract", {
        method: "POST",
        body: formData,
      });
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const saveExtraction = async () => {
    if (!token || !result || !selectedFile) return;

    setSaveLoading(true);
    setSaveMessage("");

    try {
      await apiFetch("/ocr/save", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          source_filename: selectedFile.name,
          raw_text: result.raw_text,
          structured_nutrition: result.structured_nutrition,
          image_url: result.image_url ?? null,
          image_path: result.image_path ?? null,
        }),
      });
      setIsSaved(true);
      setSaveMessage("Extraction saved to your food labels.");
      loadHistory(1);
    } catch (err) {
      setSaveMessage(err.message);
    } finally {
      setSaveLoading(false);
    }
  };

  return (
    <div className="page-card">
      <h1>Nutrition Info</h1>
      <p className="section-copy">
        Upload a nutrition label image to extract and structure its data using OCR and an LLM.
        {token
          ? " Extracted results can be saved to your food labels."
          : " Log in to save extracted labels."}
      </p>

      <form onSubmit={handleSubmit} className="form-stack">
        <div className="field-group">
          <label htmlFor="nutrition-image">Nutrition Label Image</label>
          <input
            id="nutrition-image"
            type="file"
            accept="image/*"
            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
          />
        </div>
        <button type="submit" disabled={loading || !selectedFile}>
          {loading ? "Extracting..." : "Extract Nutrition"}
        </button>
      </form>

      {error && <p className="message error">{error}</p>}

      {result && (
        <div className="recipe-card">
          <h2>Extracted Nutrition</h2>

          {imagePreviewUrl && (
            <div className="result-block" style={{ paddingTop: 0, borderTop: "none" }}>
              <img
                src={imagePreviewUrl}
                alt={selectedFile?.name ? `Preview of ${selectedFile.name}` : "Label preview"}
                className="ocr-image-preview"
              />
              <p style={{ fontSize: "0.8rem", color: "#7a92a8", margin: "0 0 0.75rem" }}>
                {selectedFile?.name}
              </p>
            </div>
          )}

          {result.structured_nutrition.product_name && (
            <p style={{ margin: "0 0 0.25rem" }}>
              <strong>{result.structured_nutrition.product_name}</strong>
              {result.structured_nutrition.serving_size && (
                <span style={{ color: "#5b6f85", fontSize: "0.9rem" }}>
                  {" "}· {result.structured_nutrition.serving_size} per serving
                </span>
              )}
            </p>
          )}

          <NutritionGrid
            nutrition={result.structured_nutrition}
            fields={ocrNutritionFields(result.structured_nutrition)}
          />

          <div className="result-block">
            <p className="section-title">Raw OCR Text</p>
            <pre className="ocr-output">{result.raw_text}</pre>
          </div>

          <hr className="card-divider" />

          {token ? (
            <div className="inline-actions">
              <button
                type="button"
                onClick={saveExtraction}
                disabled={saveLoading || isSaved}
              >
                {isSaved ? "Saved ✓" : saveLoading ? "Saving..." : "Save Extraction"}
              </button>
              {saveMessage && (
                <p className={`message ${isSaved ? "success" : "error"}`}>
                  {saveMessage}
                </p>
              )}
            </div>
          ) : (
            <p className="message">Log in to save this extraction.</p>
          )}
        </div>
      )}

      {token && (
        <div className="recipe-card" style={{ marginTop: "1rem" }}>
          <div className="history-header">
            <h2>Saved Food Labels</h2>
            {historyTotal > 0 && (
              <span className="history-badge">
                {historyTotal} {historyTotal === 1 ? "label" : "labels"}
              </span>
            )}
          </div>

          {historyLoading && <p className="section-copy">Loading...</p>}
          {historyError && <p className="message error">{historyError}</p>}
          {!historyLoading && !historyError && history.length === 0 && (
            <p className="empty-state">No saved food labels yet.</p>
          )}

          {history.map((entry) => (
            <div key={entry.id} className="result-block">
              <div className="history-header">
                <h3>{entry.source_filename}</h3>
                <span className="history-badge saved">
                  {new Date(entry.created_at).toLocaleDateString()}
                </span>
              </div>

              {entry.image_url && (
                <img
                  src={buildApiUrl(entry.image_url)}
                  alt={`Label image: ${entry.source_filename}`}
                  className="ocr-image-preview"
                  style={{ maxHeight: "200px" }}
                />
              )}

              {entry.structured_nutrition.product_name && (
                <p style={{ margin: "0 0 0.5rem", fontSize: "0.9rem" }}>
                  <strong>{entry.structured_nutrition.product_name}</strong>
                  {entry.structured_nutrition.serving_size && (
                    <span style={{ color: "#5b6f85" }}>
                      {" "}· {entry.structured_nutrition.serving_size} per serving
                    </span>
                  )}
                </p>
              )}

              <NutritionGrid
                nutrition={entry.structured_nutrition}
                fields={ocrNutritionFields(entry.structured_nutrition)}
              />
            </div>
          ))}

          {historyTotalPages > 1 && (
            <div className="pagination-bar">
              <button
                type="button"
                className="page-btn"
                disabled={historyPage <= 1 || historyLoading}
                onClick={() => loadHistory(historyPage - 1)}
              >
                ‹ Prev
              </button>
              <span className="page-info">
                Page {historyPage} of {historyTotalPages}
              </span>
              <button
                type="button"
                className="page-btn"
                disabled={historyPage >= historyTotalPages || historyLoading}
                onClick={() => loadHistory(historyPage + 1)}
              >
                Next ›
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default NutritionPage;
