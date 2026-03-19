import { useState } from "react";
import { apiFetch } from "../lib/api";

function GenerateRecipePage({ token }) {
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

    const payload = {
      ingredients: ingredients.split(",").map((i) => i.trim()).filter((i) => i !== ""),
      preferences: preferences.split(",").map((i) => i.trim()).filter((i) => i !== ""),
      allergies: allergies.split(",").map((i) => i.trim()).filter((i) => i !== ""),
    };

    try {
      const data = await apiFetch("/generate-recipe", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
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
          title: recipe.title,
          ingredients: recipe.ingredients,
          preferences: recipe.preferences,
          allergies: recipe.allergies,
          steps: recipe.steps,
          nutrition: recipe.nutrition_estimate,
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

      <label>Ingredients</label>
      <br />
      <input
        type="text"
        value={ingredients}
        onChange={(e) => setIngredients(e.target.value)}
        placeholder="e.g. chicken, rice, tomato"
      />

      <br />
      <br />

      <label>Preferences</label>
      <br />
      <input
        type="text"
        value={preferences}
        onChange={(e) => setPreferences(e.target.value)}
        placeholder="e.g. halal, vegetarian"
      />

      <br />
      <br />

      <label>Allergies</label>
      <br />
      <input
        type="text"
        value={allergies}
        onChange={(e) => setAllergies(e.target.value)}
        placeholder="e.g. peanut, milk"
      />

      <br />
      <br />

      <button onClick={generateRecipe}>Generate Recipe</button>
      {loading && <p>Generating recipe...</p>}
      {error && <p className="message error">{error}</p>}

      <p>Ingredients: {ingredients}</p>
      <p>Preferences: {preferences}</p>
      <p>Allergies: {allergies}</p>

      {recipe && (
        <div className="recipe-card">
          <h2>{recipe.title}</h2>

          <p><strong>Ingredients:</strong> {recipe.ingredients.join(", ")}</p>
          <p><strong>Preferences:</strong> {recipe.preferences.join(", ")}</p>
          <p><strong>Allergies:</strong> {recipe.allergies.join(", ")}</p>

          <h3>Steps</h3>
          <ul>
            {recipe.steps.map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ul>

          <h3>Nutrition Estimate</h3>
          <p>Calories: {recipe.nutrition_estimate.calories}</p>
          <p>Protein: {recipe.nutrition_estimate.protein}</p>
          <p>Carbs: {recipe.nutrition_estimate.carbs}</p>
          <p>Fat: {recipe.nutrition_estimate.fat}</p>

          {token ? (
            <>
              <button type="button" onClick={saveRecipe} disabled={saveLoading}>
                {saveLoading ? "Saving..." : "Save Recipe"}
              </button>
              {saveMessage && <p className="message">{saveMessage}</p>}
            </>
          ) : (
            <p className="message">Log in to save this recipe.</p>
          )}
        </div>
      )}
    </div>
  );
}

export default GenerateRecipePage;
