import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

function NutritionPage({ token }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [saveLoading, setSaveLoading] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState("");

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
          headers: {
            Authorization: `Bearer ${token}`,
          },
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

    const nextPreviewUrl = URL.createObjectURL(selectedFile);
    setImagePreviewUrl(nextPreviewUrl);

    return () => {
      URL.revokeObjectURL(nextPreviewUrl);
    };
  }, [selectedFile]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setResult(null);
    setSaveMessage("");

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
    if (!token || !result || !selectedFile) {
      return;
    }

    setSaveLoading(true);
    setSaveMessage("");

    try {
      const savedExtraction = await apiFetch("/ocr/save", {
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
      setHistory((currentHistory) => [savedExtraction, ...currentHistory]);
      setSaveMessage("Extraction saved to your OCR history.");
    } catch (err) {
      setSaveMessage(err.message);
    } finally {
      setSaveLoading(false);
    }
  };

  return (
    <div className="page-card">
      <h1>Nutrition Info</h1>
      <p className="section-copy">Upload a nutrition label image to extract and organize its nutrition data.</p>
      {token ? (
        <p className="section-copy">When you are logged in, you can save any extracted label into your OCR history.</p>
      ) : (
        <p className="section-copy">Log in if you want the extracted nutrition labels to be saved to your history.</p>
      )}

      <form onSubmit={handleSubmit} className="form-stack">
        <label htmlFor="nutrition-image">Nutrition Label Image</label>
        <input
          id="nutrition-image"
          type="file"
          accept="image/*"
          onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Extracting..." : "Extract Nutrition"}
        </button>
      </form>

      {error && <p className="message error">{error}</p>}

      {result && (
        <div className="recipe-card">
          <h2>Structured Nutrition</h2>
          {imagePreviewUrl && (
            <div className="result-block">
              <h3 className="section-title">Uploaded Label</h3>
              <img
                src={imagePreviewUrl}
                alt={selectedFile?.name ? `Preview of ${selectedFile.name}` : "Nutrition label preview"}
                className="ocr-image-preview"
              />
              {selectedFile && <p className="message">Selected file: {selectedFile.name}</p>}
            </div>
          )}

          <p><strong>Product Name:</strong> {result.structured_nutrition.product_name || "Not found"}</p>
          <p><strong>Serving Size:</strong> {result.structured_nutrition.serving_size || "Not found"}</p>
          <p><strong>Calories:</strong> {result.structured_nutrition.calories ?? "Not found"}</p>
          <p><strong>Protein (g):</strong> {result.structured_nutrition.protein_g ?? "Not found"}</p>
          <p><strong>Carbs (g):</strong> {result.structured_nutrition.carbs_g ?? "Not found"}</p>
          <p><strong>Fat (g):</strong> {result.structured_nutrition.fat_g ?? "Not found"}</p>
          <p><strong>Sugar (g):</strong> {result.structured_nutrition.sugar_g ?? "Not found"}</p>
          <p><strong>Sodium (mg):</strong> {result.structured_nutrition.sodium_mg ?? "Not found"}</p>
          <p><strong>Fiber (g):</strong> {result.structured_nutrition.fiber_g ?? "Not found"}</p>

          <h3 className="section-title">Raw OCR Text</h3>
          <pre className="ocr-output">{result.raw_text}</pre>

          {token ? (
            <div className="inline-actions">
              <button type="button" onClick={saveExtraction} disabled={saveLoading}>
                {saveLoading ? "Saving..." : "Save Extraction"}
              </button>
              {saveMessage && <p className="message">{saveMessage}</p>}
            </div>
          ) : (
            <p className="message">Log in to save this extracted nutrition data.</p>
          )}
        </div>
      )}

      {token && (
        <div className="recipe-card">
          <h2>Saved OCR History</h2>
          {historyLoading && <p>Loading saved extractions...</p>}
          {historyError && <p className="message error">{historyError}</p>}
          {!historyLoading && !historyError && history.length === 0 && (
            <p className="empty-state">No saved nutrition label extractions yet.</p>
          )}

          {history.map((entry) => (
            <div key={entry.id} className="result-block">
              <h3 className="section-title">{entry.source_filename}</h3>
              <p><strong>Saved:</strong> {new Date(entry.created_at).toLocaleString()}</p>
              <p><strong>Product Name:</strong> {entry.structured_nutrition.product_name || "Not found"}</p>
              <p><strong>Serving Size:</strong> {entry.structured_nutrition.serving_size || "Not found"}</p>
              <p><strong>Calories:</strong> {entry.structured_nutrition.calories ?? "Not found"}</p>
              <p><strong>Protein (g):</strong> {entry.structured_nutrition.protein_g ?? "Not found"}</p>
              <p><strong>Carbs (g):</strong> {entry.structured_nutrition.carbs_g ?? "Not found"}</p>
              <p><strong>Fat (g):</strong> {entry.structured_nutrition.fat_g ?? "Not found"}</p>
              <p><strong>Sugar (g):</strong> {entry.structured_nutrition.sugar_g ?? "Not found"}</p>
              <p><strong>Sodium (mg):</strong> {entry.structured_nutrition.sodium_mg ?? "Not found"}</p>
              <p><strong>Fiber (g):</strong> {entry.structured_nutrition.fiber_g ?? "Not found"}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default NutritionPage;
