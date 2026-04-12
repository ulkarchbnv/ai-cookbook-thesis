import { useState } from "react";
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
    setLoading(true);
    setError("");
    setRecipe(null);
    setSaveMessage("");
    setIsSaved(false);

    const manualPreferences = preferences.split(",").map((i) => i.trim()).filter(Boolean);
    const manualAllergies = allergies.split(",").map((i) => i.trim()).filter(Boolean);

    const payload = {
      ingredients: ingredients.split(",").map((i) => i.trim()).filter(Boolean),
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
      <p className="section-copy">
        Enter ingredients and optional dietary constraints to generate a structured recipe.
        {profile && " Your saved profile defaults apply when fields are left empty."}
      </p>

      <div className="field-grid">
        <div className="field-group">
          <label htmlFor="ingredients">Ingredients</label>
          <input
            id="ingredients"
            type="text"
            value={ingredients}
            onChange={(e) => setIngredients(e.target.value)}
            placeholder="e.g. chicken, rice, tomato"
          />
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

      <div className="button-row">
        <button type="button" onClick={generateRecipe} disabled={loading}>
          {loading ? "Generating..." : "Generate Recipe"}
        </button>
      </div>

      {error && <p className="message error">{error}</p>}

      {recipe && (
        <div className="recipe-card">
          {recipe.image_url && (
            <img
              src={buildApiUrl(recipe.image_url)}
              alt={`Thumbnail for ${recipe.title}`}
              className="recipe-image-preview"
            />
          )}

          <h2>{recipe.title}</h2>

          {recipe.warnings?.length > 0 && (
            <div style={{ marginBottom: "0.75rem" }}>
              {recipe.warnings.map((warning, index) => (
                <p key={index} className="message error">{warning}</p>
              ))}
            </div>
          )}

          <hr className="card-divider" />

          <p className="section-title">Ingredients</p>
          <div className="tag-row">
            {recipe.ingredients.map((item) => (
              <span key={item} className="tag">{item}</span>
            ))}
          </div>

          {recipe.preferences?.length > 0 && (
            <div className="tag-row" style={{ marginTop: "0.35rem" }}>
              {recipe.preferences.map((item) => (
                <span key={item} className="tag">{item}</span>
              ))}
            </div>
          )}

          {recipe.allergies?.length > 0 && (
            <div className="tag-row" style={{ marginTop: "0.35rem" }}>
              {recipe.allergies.map((item) => (
                <span key={item} className="tag allergy">{item}</span>
              ))}
            </div>
          )}

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
                {isSaved ? "Saved ✓" : saveLoading ? "Saving..." : "Save Recipe"}
              </button>
              {!recipe.generated_recipe_id && (
                <p className="message">Log in before generating to enable saving.</p>
              )}
              {saveMessage && (
                <p className={`message ${isSaved ? "success" : "error"}`}>{saveMessage}</p>
              )}
            </div>
          ) : (
            <p className="message">Log in to save this recipe.</p>
          )}
        </div>
      )}
    </div>
  );
}

export default GenerateRecipePage;