import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiFetch } from "../lib/api";
import NutritionGrid from "../components/NutritionGrid";

function NutritionPage() {
  const { token } = useAuth();
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
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

  useEffect(() => {
    if (!token) {
      setHistory([]);
      setHistoryError("");
      return;
    }

    const loadHistory = async () => {
      setHistoryLoading(true);
      setHistoryError("");
      try {
        const data = await apiFetch("/ocr/history", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setHistory(data);
      } catch (err) {
        setHistoryError(err.message);
      } finally {
        setHistoryLoading(false);
      }
    };

    loadHistory();
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
      const saved = await apiFetch("/ocr/save", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          source_filename: selectedFile.name,
          raw_text: result.raw_text,
          structured_nutrition: result.structured_nutrition,
        }),
      });
      setHistory((prev) => [saved, ...prev]);
      setIsSaved(true);
      setSaveMessage("Extraction saved to your history.");
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
          ? " Extracted results can be saved to your history."
          : " Log in to save extracted labels to your history."}
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
          <h2>OCR History</h2>

          {historyLoading && <p className="section-copy">Loading...</p>}
          {historyError && <p className="message error">{historyError}</p>}
          {!historyLoading && !historyError && history.length === 0 && (
            <p className="empty-state">No saved extractions yet.</p>
          )}

          {history.map((entry) => (
            <div key={entry.id} className="result-block">
              <div className="history-header">
                <h3>{entry.source_filename}</h3>
                <span className="history-badge saved">
                  {new Date(entry.created_at).toLocaleDateString()}
                </span>
              </div>

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
        </div>
      )}
    </div>
  );
}

export default NutritionPage;
