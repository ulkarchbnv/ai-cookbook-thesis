import { useState } from "react";
import { apiFetch } from "../lib/api";

function NutritionPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setResult(null);

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

  return (
    <div className="page-card">
      <h1>Nutrition Info</h1>
      <p>Upload a nutrition label image and the system will extract text and structure it.</p>
      <p>
        This follows the thesis design directly: OCR reads the label first, then the application
        turns the raw text into clean nutrition data.
      </p>

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
          <p><strong>Product Name:</strong> {result.structured_nutrition.product_name || "Not found"}</p>
          <p><strong>Serving Size:</strong> {result.structured_nutrition.serving_size || "Not found"}</p>
          <p><strong>Calories:</strong> {result.structured_nutrition.calories ?? "Not found"}</p>
          <p><strong>Protein (g):</strong> {result.structured_nutrition.protein_g ?? "Not found"}</p>
          <p><strong>Carbs (g):</strong> {result.structured_nutrition.carbs_g ?? "Not found"}</p>
          <p><strong>Fat (g):</strong> {result.structured_nutrition.fat_g ?? "Not found"}</p>
          <p><strong>Sugar (g):</strong> {result.structured_nutrition.sugar_g ?? "Not found"}</p>
          <p><strong>Sodium (mg):</strong> {result.structured_nutrition.sodium_mg ?? "Not found"}</p>
          <p><strong>Fiber (g):</strong> {result.structured_nutrition.fiber_g ?? "Not found"}</p>

          <h3>Raw OCR Text</h3>
          <pre className="ocr-output">{result.raw_text}</pre>
        </div>
      )}
    </div>
  );
}

export default NutritionPage;
