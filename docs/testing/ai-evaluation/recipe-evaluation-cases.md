# Recipe Evaluation Cases

Use these cases to evaluate the combined behavior of:

- input handling
- RAG retrieval quality
- LLM response structure
- preference/allergy constraint satisfaction
- practical usefulness of the generated recipe

For each case, run the generation through the real application and fill the CSV result sheet.

## Scoring Rules

- `structure_valid`: `1` if title, ingredient list, steps, and nutrition estimate are all present in usable form, else `0`
- `allergy_safe`: `1` if no forbidden ingredient appears in title or ingredient list, else `0`
- `preference_satisfied`: `1` if the output respects the dietary rule, else `0`
- `ingredient_coverage_score`: score from `0` to `1`
  - `1.0`: most provided ingredients are meaningfully used
  - `0.5`: some ingredients are used but important ones are ignored
  - `0.0`: poor use of provided ingredients
- `practical_quality_score`: integer `1` to `5`
  - `5`: highly usable and coherent
  - `3`: acceptable but imperfect
  - `1`: poor or unusable

## Cases

### R-01 Basic Vegetarian Pasta

- Ingredients: `tomato, basil, pasta`
- Preferences: `vegetarian`
- Allergies: `peanut`
- Purpose: baseline structured generation
- Expected properties:
  - no peanut ingredients
  - suitable vegetarian meal
  - sensible use of pasta/tomato/basil

### R-02 Sparse Pantry Input

- Ingredients: `egg, bread, cheese`
- Preferences: none
- Allergies: none
- Purpose: test generation quality with minimal household ingredients
- Expected properties:
  - recipe remains practical
  - limited unnecessary additions

### R-03 Vegan Constraint

- Ingredients: `tofu, mushroom, rice, soy sauce`
- Preferences: `vegan`
- Allergies: none
- Purpose: verify vegan filtering and suitable retrieval/generation
- Expected properties:
  - no meat, egg, milk, cheese, butter, cream, or honey

### R-04 Peanut Allergy Protection

- Ingredients: `chicken, rice, peanut butter`
- Preferences: none
- Allergies: `peanut`
- Purpose: verify conflict filtering and warning behavior
- Expected properties:
  - peanut ingredient excluded or warned about
  - recipe remains coherent after exclusion

### R-05 Vegetarian Conflict Input

- Ingredients: `chicken, tomato, onion`
- Preferences: `vegetarian`
- Allergies: none
- Purpose: verify preference-conflict filtering
- Expected properties:
  - chicken excluded or explicitly warned
  - output remains vegetarian

### R-06 Halal Preference

- Ingredients: `beef, onion, tomato, rice`
- Preferences: `halal`
- Allergies: none
- Purpose: check compatibility with halal-friendly input
- Expected properties:
  - no pork-derived additions

### R-07 Milk Allergy

- Ingredients: `oats, banana, milk`
- Preferences: none
- Allergies: `milk`
- Purpose: verify dairy-allergy conflict handling
- Expected properties:
  - milk excluded or warned about
  - recipe still usable

### R-08 Vegan and Nut-Safe Breakfast

- Ingredients: `oats, banana, strawberry`
- Preferences: `vegan`
- Allergies: `tree nut`
- Purpose: combined preference + allergy case
- Expected properties:
  - no dairy or nut ingredients
  - breakfast-style output is acceptable

### R-09 Seafood Allergy

- Ingredients: `shrimp, garlic, pasta`
- Preferences: none
- Allergies: `shellfish`
- Purpose: verify allergy conflict removal in seafood case
- Expected properties:
  - shrimp excluded or warning issued
  - output does not contain shellfish

### R-10 Low-Context Simple Salad

- Ingredients: `cucumber, tomato, lettuce, lemon`
- Preferences: `vegetarian`
- Allergies: none
- Purpose: test simple fresh recipe generation
- Expected properties:
  - output remains simple and coherent
  - no unnecessary heavy ingredients

### R-11 All Ingredients Conflict

- Ingredients: `milk, cheese, butter`
- Preferences: `vegan`
- Allergies: `milk`
- Purpose: test failure behavior when all inputs conflict
- Expected properties:
  - request should fail cleanly or clearly reject unsafe generation

### R-12 Ingredient Drift Check

- Ingredients: `rice, carrot, onion`
- Preferences: none
- Allergies: none
- Purpose: observe how many extra ingredients are introduced
- Expected properties:
  - additional ingredients are limited
  - recipe still centers user input

## Aggregated Metrics to Compute

- total cases
- successful responses
- structure validity rate
- allergy safety rate
- preference satisfaction rate
- average ingredient coverage score
- average practical quality score
- average additional ingredient count
