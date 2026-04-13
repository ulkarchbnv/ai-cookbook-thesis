function NutritionGrid({ nutrition, fields }) {
  const defaultFields = [
    { label: "Calories", value: nutrition.calories },
    { label: "Protein", value: nutrition.protein },
    { label: "Carbs", value: nutrition.carbs },
    { label: "Fat", value: nutrition.fat },
  ];

  const resolvedFields = fields ?? defaultFields;

  return (
    <div className="nutrition-grid">
      {resolvedFields.map(({ label, value }) => (
        <div key={label} className="nutrition-cell">
          <div className="cell-label">{label}</div>
          <div className="cell-value">{value ?? "—"}</div>
        </div>
      ))}
    </div>
  );
}

export default NutritionGrid;
