import { useState } from "react";
import { apiFetch, buildApiUrl } from "../lib/api";

function GenerateRecipePage({ token, profile }) {
  const [ingredients, setIngredients] = useState("");
  const [preferences, setPreferences] = useState("");
  const [allergies, setAllergies] = useState("");
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [saveMessage, setSaveMessage] = useState("");
  const [saveLoading, setSaveLoading] = useState(false);

  const generateRecipe = async () => {
    setLoading(true);
    setError("");
    setRecipe(null);
    setSaveMessage("");

    const manualPreferences = preferences.split(",").map((i) => i.trim()).filter((i) => i !== "");
    const manualAllergies = allergies.split(",").map((i) => i.trim()).filter((i) => i !== "");

    const payload = {
      ingredients: ingredients.split(",").map((i) => i.trim()).filter((i) => i !== ""),
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
    if (!recipe || !token) {
      return;
    }

    setSaveLoading(true);
    setSaveMessage("");

    try {
      await apiFetch("/recipes", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          generated_recipe_id: recipe.generated_recipe_id,
        }),
      });

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
      </p>

      {profile && (
        <p className="section-copy">
          Saved profile defaults will be used when the preference or allergy fields are left empty.
        </p>
      )}

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
          <label htmlFor="preferences">Preferences</label>
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
        <button type="button" onClick={generateRecipe}>Generate Recipe</button>
      </div>
      {loading && <p>Generating recipe...</p>}
      {error && <p className="message error">{error}</p>}

      {recipe && (
        <div className="recipe-card">
          <h2>{recipe.title}</h2>
          {recipe.image_url && (
            <img
              src={buildApiUrl(recipe.image_url)}
              alt={`Generated thumbnail for ${recipe.title}`}
              className="recipe-image-preview"
            />
          )}
          {recipe.warnings?.map((warning, index) => (
            <p key={index} className="message">
              {warning}
            </p>
          ))}
          <p><strong>Ingredients:</strong> {recipe.ingredients.join(", ")}</p>
          <p><strong>Preferences:</strong> {recipe.preferences.join(", ") || "None"}</p>
          <p><strong>Allergies:</strong> {recipe.allergies.join(", ") || "None"}</p>

          <div className="result-block">
            <h3 className="section-title">Steps</h3>
            <ul className="result-list">
              {recipe.steps.map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ul>
          </div>

          <p><strong>Calories:</strong> {recipe.nutrition_estimate.calories}</p>
          <p><strong>Protein:</strong> {recipe.nutrition_estimate.protein}</p>
          <p><strong>Carbs:</strong> {recipe.nutrition_estimate.carbs}</p>
          <p><strong>Fat:</strong> {recipe.nutrition_estimate.fat}</p>

          {token ? (
            <div className="inline-actions">
              <button
                type="button"
                onClick={saveRecipe}
                disabled={saveLoading || !recipe.generated_recipe_id}
              >
                {saveLoading ? "Saving..." : "Save Recipe"}
              </button>
              {!recipe.generated_recipe_id && (
                <p className="message">Generate while logged in to store this recipe in your history and save it.</p>
              )}
              {saveMessage && <p className="message">{saveMessage}</p>}
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
