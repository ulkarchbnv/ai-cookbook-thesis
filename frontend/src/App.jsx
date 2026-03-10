import {useState} from "react";

function App() {
  const [ingredients, setIngredients] = useState("");
  const [preferences, setPreferences] = useState("");
  const [allergies, setAllergies] = useState("");
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generateRecipe = async () => 
  {
    setLoading(true);
    setError("");
    setRecipe(null);
    console.log("Button clicked");
    const load = 
    {
      ingredients: ingredients.split(",").map((i) => i.trim()).filter(i => i !== ""),
      preferences: preferences.split(",").map((i) => i.trim()).filter(i => i !== ""),
      allergies: allergies.split(",").map((i) => i.trim()).filter(i => i !== ""),
      
    };
    console.log("Payload being sent: ", load);
    try{
      const response = await fetch("http://127.0.0.1:8000/generate-recipe", 
        {
          method: "POST",
          headers: 
          {
            "Content-type": "application/json"
          },
          body: JSON.stringify(load)
        }
      );
      if (!response.ok) {
        throw new Error("Failed to generate recipe");
      }

      const data = await response.json();
      console.log("Response from backend:", data);
      setRecipe(data);
    } catch (err) {
      console.error("Frontend error:", err);
      setError(err.message);
    } finally {
      setLoading(false);
  }};
  return (
    <div>      <h1>AI Cookbook</h1>
      <label>Ingredients</label>
      <br />
      <input
      type = "text"
      value = {ingredients}
      onChange = {(e) => setIngredients(e.target.value)}
      placeholder = "e.g. chicken, rice, tomato"
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
      <button onClick = {generateRecipe}>Generate Recipe</button>
      {loading && <p>Generating recipe...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      <p>Ingredients: {ingredients}</p>
      <p>Preferences: {preferences}</p>
      <p>Allergies: {allergies}</p>
            {recipe && (
        <div>
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
        </div>
      )}
    </div>
  );
}
export default App;