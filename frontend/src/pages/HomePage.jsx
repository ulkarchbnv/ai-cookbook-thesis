function HomePage() {
  return (
    <div className="page-card">
      <h1>AI Cookbook</h1>
      <p className="section-copy">
        Generate practical recipes from available ingredients, adapt them for dietary needs,
        and extract nutrition details from food labels — all in one place.
      </p>

      <div className="meta-grid">
        <div className="meta-card">
          <strong>Recipe Generation</strong>
          <p>
            Enter ingredients and dietary constraints. The system retrieves relevant
            context from a recipe knowledge base using RAG before generating a structured result.
          </p>
        </div>
        <div className="meta-card">
          <strong>Food Label Scanner</strong>
          <p>
            Upload a nutrition label image. Google Vision extracts the text and an LLM
            converts it into structured nutrition fields. Saved labels are stored with
            their original image for later review.
          </p>
        </div>
        <div className="meta-card">
          <strong>Saved Recipes &amp; History</strong>
          <p>
            Logged-in users can save generated recipes, browse full generation
            history, and review past food label extractions — all paginated.
          </p>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
