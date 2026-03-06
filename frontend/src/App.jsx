import {useState} from "react";
function App() {
  const [ingredients, setIngredients] = useState("");
  const [preferences, setPreferences] = useState("");
  const [allergies, setAllergies] = useState("");
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
      <button>Generate Recipe</button>
      <p>Ingredients: {ingredients}</p>
      <p>Preferences: {preferences}</p>
      <p>Allergies: {allergies}</p>
    </div>
  );
}
export default App;