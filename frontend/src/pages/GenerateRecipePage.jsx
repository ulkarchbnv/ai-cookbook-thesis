import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiFetch, buildApiUrl } from "../lib/api";
import NutritionGrid from "../components/NutritionGrid";

function GenerateRecipePage() {
  const { token, profile } = useAuth();
  const [ingredients, setIngredients] = useState("");
  const [preferences, setPreferences] = useState("");
  const [allergies, setAllergies] = useState("");
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [saveMessage, setSaveMessage] = useState("");
  const [saveLoading, setSaveLoading] = useState(false);
  const [isSaved, setIsSaved] = useState(false);

  const generateRecipe = async () => {
    const parsedIngredients = ingredients.split(",").map((i) => i.trim()).filter(Boolean);
    if (parsedIngredients.length === 0) {
      setError("Please enter at least one ingredient.");
      return;
    }

    setLoading(true);
    setError("");
    setRecipe(null);
    setSaveMessage("");
    setIsSaved(false);

    const manualPreferences = preferences.split(",").map((i) => i.trim()).filter(Boolean);
    const manualAllergies = allergies.split(",").map((i) => i.trim()).filter(Boolean);

    const payload = {
      ingredients: parsedIngredients,
      preferences: manualPreferences.length > 0 ? manualPreferences : profile?.preferences || [],
      allergies: manualAllergies.length > 0 ? manualAllergies : profile?.allergies || [],
    };

    try {
      const data = await apiFetch("/generate-recipe", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(payload),
      });
      setRecipe(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const saveRecipe = async () => {
    if (!recipe || !token) return;

    setSaveLoading(true);
    setSaveMessage("");

    try {
      await apiFetch("/recipes", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ generated_recipe_id: recipe.generated_recipe_id }),
      });
      setIsSaved(true);
      setSaveMessage("Recipe saved successfully.");
    } catch (err) {
      setSaveMessage(err.message);
    } finally {
      setSaveLoading(false);
    }
  };

  return (
    <div className="page-card">
      <h1>Generate Recipe</h1>
      <p className="page-subtitle">
        List your available ingredients below. The system uses retrieval-augmented
        generation to create a structured recipe using only what you provide.
        {profile && " Your saved profile defaults apply when fields are left empty."}
      </p>

      <div className="field-grid">
        <div className="field-group" style={{ gridColumn: "1 / -1" }}>
          <label htmlFor="ingredients">Ingredients *</label>
          <input
            id="ingredients"
            type="text"
            value={ingredients}
            onChange={(e) => setIngredients(e.target.value)}
            placeholder="e.g. chicken, rice, tomato, onion"
          />
          <p className="field-hint">Separate with commas. Up to 25 ingredients.</p>
        </div>
        <div className="field-group">
          <label htmlFor="preferences">Dietary Preferences</label>
          <input
            id="preferences"
            type="text"
            value={preferences}
            onChange={(e) => setPreferences(e.target.value)}
            placeholder="e.g. halal, vegetarian"
          />
        </div>
        <div className="field-group">
          <label htmlFor="allergies">Allergies</label>
          <input
            id="allergies"
            type="text"
            value={allergies}
            onChange={(e) => setAllergies(e.target.value)}
            placeholder="e.g. peanut, milk"
          />
        </div>
      </div>

      <button type="button" onClick={generateRecipe} disabled={loading}>
        {loading ? "Generating..." : "Generate Recipe"}
      </button>

      {error && <p className="message error" style={{ marginTop: "0.75rem" }}>{error}</p>}

      {recipe && (
        <div className="recipe-card" style={{ marginTop: "1rem" }}>
          <div className="recipe-hero">
            {recipe.image_url && (
              <img
                src={buildApiUrl(recipe.image_url)}
                alt={`Thumbnail for ${recipe.title}`}
                className="recipe-image-preview"
              />
            )}
            <div>
              <h2>{recipe.title}</h2>

              {recipe.warnings?.length > 0 && (
                <div style={{ marginBottom: "0.5rem" }}>
                  {recipe.warnings.map((warning, index) => (
                    <div key={index} className="alert-box warning" style={{ marginBottom: "0.35rem" }}>
                      {warning}
                    </div>
                  ))}
                </div>
              )}

              <p className="section-label">Ingredients</p>
              <div className="tag-row">
                {recipe.ingredients
                  .filter((item) => !(recipe.additional_ingredients || []).includes(item))
                  .map((item, index) => (
                    <span key={index} className="tag">{item}</span>
                  ))}
              </div>
              {recipe.additional_ingredients?.length > 0 && (
                <div style={{ marginTop: "0.5rem" }}>
                  <p className="section-label">You may also need</p>
                  <div className="tag-row">
                    {recipe.additional_ingredients.map((item, index) => (
                      <span key={index} className="tag additional">{item}</span>
                    ))}
                  </div>
                </div>
              )}

              {recipe.preferences?.length > 0 && (
                <div style={{ marginTop: "0.5rem" }}>
                  <p className="section-label">Preferences</p>
                  <div className="tag-row">
                    {recipe.preferences.map((item, index) => (
                      <span key={index} className="tag preference">{item}</span>
                    ))}
                  </div>
                </div>
              )}

              {recipe.allergies?.length > 0 && (
                <div style={{ marginTop: "0.5rem" }}>
                  <p className="section-label">Allergies</p>
                  <div className="tag-row">
                    {recipe.allergies.map((item, index) => (
                      <span key={index} className="tag allergy">{item}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="result-block">
            <p className="section-title">Preparation Steps</p>
            <ol className="result-list">
              {recipe.steps.map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ol>
          </div>

          <div className="result-block">
            <p className="section-title">Nutrition Estimate</p>
            <NutritionGrid nutrition={recipe.nutrition_estimate} />
          </div>

          <hr className="card-divider" />

          {token ? (
            <div className="inline-actions">
              <button
                type="button"
                onClick={saveRecipe}
                disabled={saveLoading || isSaved || !recipe.generated_recipe_id}
              >
                {isSaved ? "Saved \u2713" : saveLoading ? "Saving..." : "Save Recipe"}
              </button>
              {!recipe.generated_recipe_id && (
                <p className="message">Log in before generating to enable saving.</p>
              )}
              {saveMessage && (
                <p className={`message ${isSaved ? "success" : "error"}`}>{saveMessage}</p>
              )}
            </div>
          ) : (
            <p className="message" style={{ marginTop: "0.5rem" }}>Log in to save this recipe.</p>
          )}
        </div>
      )}
    </div>
  );
}

export default GenerateRecipePage;
