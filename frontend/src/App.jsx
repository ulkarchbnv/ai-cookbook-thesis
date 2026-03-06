import {useState} from "react";
function App() {
  const [ingredients, setIngredients] = useState("");
  const [preferences, setPreferences] = useState("");
  const [allergies, setAllergies] = useState("");
  const generateRecipe = async () => 
  {
    console.log("Button clicked");
    const load = 
    {
      ingredients: ingredients.split(",").map((i) => i.trim()).filter(i => i !== ""),
      preferences: preferences.split(",").map((i) => i.trim()).filter(i => i !== ""),
      allergies: allergies.split(",").map((i) => i.trim()).filter(i => i !== ""),
      
    };
    console.log("Payload being sent: ", load)
  };
  return (
    <div>
      <h1>AI Cookbook</h1>
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
      <p>Ingredients: {ingredients}</p>
      <p>Preferences: {preferences}</p>
      <p>Allergies: {allergies}</p>
    </div>
  );
}
export default App;