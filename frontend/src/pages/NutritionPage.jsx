import { useEffect, useState, useRef } from "react";
import { useAuth } from "../context/AuthContext";
import { apiFetch, buildApiUrl } from "../lib/api";
import NutritionGrid from "../components/NutritionGrid";

const PAGE_SIZE = 10;

function NutritionPage() {
  const { token } = useAuth();
  const fileInputRef = useRef(null);
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
      <h1>Food Labels</h1>
      <p className="page-subtitle">
        Upload a photo of a nutrition label to extract structured data using OCR and an LLM.
        {token
          ? " Results can be saved to your label history with the original image."
          : " Log in to save extractions to your history."}
      </p>

      <form onSubmit={handleSubmit}>
        <div
          className={`file-drop-zone${selectedFile ? " has-file" : ""}`}
          onClick={() => fileInputRef.current?.click()}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") fileInputRef.current?.click(); }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            style={{ display: "none" }}
            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
          />
          {selectedFile ? (
            <>
              <span className="drop-icon" aria-hidden="true">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              </span>
              <span className="drop-text">{selectedFile.name}</span>
              <span className="drop-hint">Click to change file</span>
            </>
          ) : (
            <>
              <span className="drop-icon" aria-hidden="true">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/></svg>
              </span>
              <span className="drop-text">Click to select a nutrition label image</span>
              <span className="drop-hint">JPG, PNG, WebP · Max 5 MB</span>
            </>
          )}
        </div>

        <div style={{ marginTop: "0.75rem" }}>
          <button type="submit" disabled={loading || !selectedFile}>
            {loading ? "Extracting..." : "Extract Nutrition"}
          </button>
        </div>
      </form>

      {error && <p className="message error" style={{ marginTop: "0.5rem" }}>{error}</p>}

      {result && (
        <div className="recipe-card" style={{ marginTop: "1rem" }}>
          <h2>Extracted Nutrition</h2>

          {imagePreviewUrl && (
            <div style={{ marginBottom: "0.5rem" }}>
              <img
                src={imagePreviewUrl}
                alt={selectedFile?.name ? `Preview of ${selectedFile.name}` : "Label preview"}
                className="ocr-image-preview"
              />
              <p className="history-meta" style={{ margin: 0 }}>{selectedFile?.name}</p>
            </div>
          )}

          {result.structured_nutrition.product_name && (
            <p style={{ margin: "0.5rem 0 0.25rem" }}>
              <strong>{result.structured_nutrition.product_name}</strong>
              {result.structured_nutrition.serving_size && (
                <span style={{ color: "var(--color-text-secondary)", fontSize: "0.85rem" }}>
                  {" "}\u00B7 {result.structured_nutrition.serving_size} per serving
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
                {isSaved ? "Saved \u2713" : saveLoading ? "Saving..." : "Save to Food Labels"}
              </button>
              {saveMessage && (
                <p className={`message ${isSaved ? "success" : "error"}`}>
                  {saveMessage}
                </p>
              )}
            </div>
          ) : (
            <p className="message" style={{ marginTop: "0.5rem" }}>Log in to save this extraction.</p>
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

          {historyLoading && <div className="loading-bar">Loading labels...</div>}
          {historyError && <p className="message error">{historyError}</p>}
          {!historyLoading && !historyError && history.length === 0 && (
            <div className="empty-state">
              <span className="empty-state-icon" aria-hidden="true">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>
              </span>
              No saved food labels yet. Extract a label above and save it.
            </div>
          )}

          {history.map((entry) => (
            <div key={entry.id} className="result-block">
              <div className="history-header">
                <h3>
                  {entry.structured_nutrition?.product_name || entry.source_filename}
                </h3>
                <span className="history-badge saved">
                  {new Date(entry.created_at).toLocaleDateString()}
                </span>
              </div>

              {entry.image_url && (
                <img
                  src={buildApiUrl(entry.image_url)}
                  alt={`Label image: ${entry.source_filename}`}
                  className="ocr-image-preview"
                  style={{ maxHeight: "180px" }}
                />
              )}

              {entry.structured_nutrition?.product_name && (
                <p style={{ margin: "0 0 0.35rem", fontSize: "0.825rem" }}>
                  <strong>{entry.structured_nutrition.product_name}</strong>
                  {entry.structured_nutrition.serving_size && (
                    <span style={{ color: "var(--color-text-secondary)" }}>
                      {" "}\u00B7 {entry.structured_nutrition.serving_size} per serving
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
                &#8249; Prev
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
                Next &#8250;
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default NutritionPage;
