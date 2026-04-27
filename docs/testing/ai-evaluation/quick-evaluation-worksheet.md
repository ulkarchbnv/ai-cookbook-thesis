# Quick AI Evaluation Worksheet

This worksheet is a compact execution guide for the strongest thesis-ready
AI evaluation cases. It is intended to reduce friction while filling:

- `recipe-evaluation-results.csv`
- `ocr-evaluation-results.csv`



---

## 1. Recipe Generation Evaluation

Recommended minimum thesis set:

- `R-01` baseline success
- `R-04` allergy handling
- `R-05` preference-conflict handling
- `R-11` clean rejection/failure behavior
- `R-12` ingredient drift / additional ingredient control

### Recipe scoring legend

- `response_status`: `success`, `rejected`, `failed`, or `error`
- `structure_valid`: `1` if title, ingredients, steps, and nutrition estimate are all usable, else `0`
- `allergy_safe`: `1` if no forbidden ingredient appears, else `0`
- `preference_satisfied`: `1` if dietary rule is respected, else `0`
- `ingredient_coverage_score`: `1.0`, `0.5`, or `0.0`
- `additional_ingredient_count`: integer count
- `practical_quality_score`: integer `1` to `5`
- `warnings_present`: `1` or `0`
- `error_present`: `1` or `0`

### R-01 Basic Vegetarian Pasta

- Ingredients: `tomato, basil, pasta`
- Preferences: `vegetarian`
- Allergies: `peanut`
- Check:
  - no peanut ingredient
  - still vegetarian
  - uses tomato, basil, and pasta meaningfully
- Fill:
  - `response_status =`
  - `structure_valid =`
  - `allergy_safe =`
  - `preference_satisfied =`
  - `ingredient_coverage_score =`
  - `additional_ingredient_count =`
  - `practical_quality_score =`
  - `warnings_present =`
  - `error_present =`
  - `notes =`

### R-04 Peanut Allergy Protection

- Ingredients: `chicken, rice, peanut butter`
- Preferences: none
- Allergies: `peanut`
- Check:
  - peanut ingredient excluded or warning shown
  - recipe remains coherent after exclusion
- Fill:
  - `response_status =`
  - `structure_valid =`
  - `allergy_safe =`
  - `preference_satisfied =`
  - `ingredient_coverage_score =`
  - `additional_ingredient_count =`
  - `practical_quality_score =`
  - `warnings_present =`
  - `error_present =`
  - `notes =`

### R-05 Vegetarian Conflict Input

- Ingredients: `chicken, tomato, onion`
- Preferences: `vegetarian`
- Allergies: none
- Check:
  - chicken excluded or warning shown
  - final output remains vegetarian
- Fill:
  - `response_status =`
  - `structure_valid =`
  - `allergy_safe =`
  - `preference_satisfied =`
  - `ingredient_coverage_score =`
  - `additional_ingredient_count =`
  - `practical_quality_score =`
  - `warnings_present =`
  - `error_present =`
  - `notes =`

### R-11 All Ingredients Conflict

- Ingredients: `milk, cheese, butter`
- Preferences: `vegan`
- Allergies: `milk`
- Check:
  - request should fail cleanly or reject unsafe generation
- Fill:
  - `response_status =`
  - `structure_valid =`
  - `allergy_safe =`
  - `preference_satisfied =`
  - `ingredient_coverage_score =`
  - `additional_ingredient_count =`
  - `practical_quality_score =`
  - `warnings_present =`
  - `error_present =`
  - `notes =`

### R-12 Ingredient Drift Check

- Ingredients: `rice, carrot, onion`
- Preferences: none
- Allergies: none
- Check:
  - extra ingredients should remain limited
  - recipe should still center the user input
- Fill:
  - `response_status =`
  - `structure_valid =`
  - `allergy_safe =`
  - `preference_satisfied =`
  - `ingredient_coverage_score =`
  - `additional_ingredient_count =`
  - `practical_quality_score =`
  - `warnings_present =`
  - `error_present =`
  - `notes =`

### Recommended screenshots for recipe AI testing

- one successful baseline generation (`R-01`)
- one allergy-handling case (`R-04`)
- one preference-conflict case (`R-05`)
- one clean failure/rejection (`R-11`)
- one ingredient-drift case (`R-12`)

---

## 2. OCR Evaluation

Recommended minimum thesis set:

- `O-01` clear nutrition label
- `O-02` alternate label layout
- `O-03` real-world photo

### OCR scoring legend

- `ocr_success`: `1` if OCR produced usable raw text, else `0`
- `structured_output_success`: `1` if structured nutrition output was produced, else `0`
- each `*_correct` field: `1` or `0`
- `correct_field_count`: count of correct fields among:
  - product name
  - serving size
  - calories
  - protein
  - carbs
  - fat
  - sugar
  - sodium
  - fiber

### O-01 Clear Nutrition Label

- Image: `nutrition-facts.jpg`
- Check:
  - OCR succeeds
  - most numeric fields are correct
- Fill:
  - `ocr_success =`
  - `structured_output_success =`
  - `product_name_expected =`
  - `product_name_observed =`
  - `product_name_correct =`
  - `serving_size_expected =`
  - `serving_size_observed =`
  - `serving_size_correct =`
  - `calories_expected =`
  - `calories_observed =`
  - `calories_correct =`
  - `protein_expected =`
  - `protein_observed =`
  - `protein_correct =`
  - `carbs_expected =`
  - `carbs_observed =`
  - `carbs_correct =`
  - `fat_expected =`
  - `fat_observed =`
  - `fat_correct =`
  - `sugar_expected =`
  - `sugar_observed =`
  - `sugar_correct =`
  - `sodium_expected =`
  - `sodium_observed =`
  - `sodium_correct =`
  - `fiber_expected =`
  - `fiber_observed =`
  - `fiber_correct =`
  - `correct_field_count =`
  - `notes =`

### O-02 Alternate Label Layout

- Image: `unnamed.jpg`
- Check:
  - OCR should still return structured values
  - layout differences may cause field confusion
- Fill the same fields as above.

### O-03 Real-World Camera Photo

- Image: `WhatsApp Image 2026-04-14 at 13.56.17.jpeg`
- Check:
  - OCR may degrade slightly
  - key fields should still be recoverable if readable
- Fill the same fields as above.

### Recommended screenshots for OCR AI testing

- original label image
- successful OCR result page
- raw OCR text
- structured output
- one weak or partially incorrect case

---

## 3. Metrics to Compute Afterwards

### Recipe metrics

- total cases
- successful responses
- structure validity rate
- allergy safety rate
- preference satisfaction rate
- average ingredient coverage score
- average additional ingredient count
- average practical quality score

### OCR metrics

- total images tested
- OCR success rate
- structured output success rate
- calories exact-match rate
- macro exact-match rate
- average correct fields per image
- high-quality extraction rate

---



For each weak case, note whether the problem came from:

- input quality
- OCR reading quality
- numeric parsing
- field mapping / structuring
- dietary or allergy rule handling
- excessive ingredient drift

These short notes become the error-analysis paragraph later.
