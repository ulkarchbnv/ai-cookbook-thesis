import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function HomePage() {
  const { token } = useAuth();

  return (
    <div className="page-card">
      <div className="hero-split">
        <div className="hero-editorial">
          <p className="hero-eyebrow">RAG · OCR · LLM-Based Personalization</p>
          <h1>AI Cookbook with Ingredient-Based Search</h1>
          <p className="page-subtitle">
            An AI-powered system that generates structured recipes from user-provided ingredients,
            integrates OCR-based nutritional data extraction from food labels, and adapts outputs
            based on dietary preferences and allergen constraints.
          </p>
        </div>
        <div className="hero-cta-col">
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
          <span className="feature-num">01</span>
          <strong>Structured Recipe Generation &amp; Personalisation</strong>
          <p>
            Generates structured recipes with ingredients, preparation steps,
            and nutritional details using retrieval-augmented generation (RAG), personalised
            to dietary restrictions and allergen preferences.
          </p>
        </div>
        <div className="feature-card">
          <span className="feature-num">02</span>
          <strong>OCR-Based Nutrition Label Processing</strong>
          <p>
            Upload an image of any food label. Text is extracted via Google
            Cloud Vision OCR and refined by a language model into structured JSON for
            consistent interpretation of nutritional values.
          </p>
        </div>
        <div className="feature-card">
          <span className="feature-num">03</span>
          <strong>Data Persistence &amp; Backend Integration</strong>
          <p>
            A lightweight backend handles recipe generation requests and
            manages user data. Preferences, generated recipes, and interaction history
            are stored for improved continuity and usability.
          </p>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
