function HomePage() {
  return (
    <div className="page-card">
      <h1>AI Cookbook</h1>
      <p className="section-copy">
        Generate practical recipes from available ingredients, adapt them for dietary needs, and
        extract nutrition details from food labels in one place.
      </p>

      <div className="meta-grid">
        <div className="meta-card">
          <strong>Recipe Generation</strong>
          Create structured recipes from ingredients, preferences, and allergy constraints.
        </div>
        <div className="meta-card">
          <strong>Nutrition OCR</strong>
          Upload a food label image and convert it into usable nutrition fields.
        </div>
        <div className="meta-card">
          <strong>Saved Results</strong>
          Keep generated recipes available for later review and comparison.
        </div>
      </div>
    </div>
  );
}

export default HomePage;
