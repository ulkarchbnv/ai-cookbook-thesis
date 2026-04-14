import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function HomePage() {
  const { token } = useAuth();

  return (
    <div className="page-card">
      <div className="hero-section">
        <h1>AI Cookbook</h1>
        <p className="page-subtitle" style={{ margin: "0 auto 0.5rem", textAlign: "center" }}>
          Generate structured recipes from the ingredients you already have,
          scan nutrition labels for instant data extraction, and keep
          everything organized in your personal cooking history.
        </p>
        <div className="hero-actions">
          <Link to="/generate">
            <button type="button">Generate a Recipe</button>
          </Link>
          <Link to="/nutrition">
            <button type="button" className="secondary">Scan a Food Label</button>
          </Link>
        </div>
      </div>

      <div className="feature-grid">
        <div className="feature-card">
          <div className="feature-icon" aria-hidden="true">&#x1F952;</div>
          <strong>Ingredient-Based Recipes</strong>
          <p>
            Enter what you have on hand. The system retrieves relevant context
            from a recipe knowledge base (RAG) and generates a structured recipe
            using only your ingredients.
          </p>
        </div>
        <div className="feature-card">
          <div className="feature-icon" aria-hidden="true">&#x1F4F7;</div>
          <strong>Food Label Scanner</strong>
          <p>
            Upload a photo of any nutrition label. Google Vision extracts the text,
            then an LLM structures it into calories, protein, carbs, fat, and more.
          </p>
        </div>
        <div className="feature-card">
          <div className="feature-icon" aria-hidden="true">&#x1F4BE;</div>
          <strong>Save &amp; Review</strong>
          <p>
            {token
              ? "Your recipes and food labels are saved with images and full history, all paginated for easy browsing."
              : "Log in to save recipes, track generation history, and review past food label scans with original images."}
          </p>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
