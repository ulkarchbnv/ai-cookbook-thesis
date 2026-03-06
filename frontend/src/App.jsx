import {useState} from "react";
function App() {
  const [ingredients, setIngredients] = useState("");
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
    </div>
  );
}
export default App;