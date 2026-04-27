# Metric Calculation Notes

This file explains how to turn the filled evaluation CSV files into thesis metrics.

## Recipe Metrics

Using `recipe-evaluation-results.csv`:

- `total_cases` = number of rows
- `successful_responses` = count where `response_status` indicates successful generation
- `structure_validity_rate` = sum(`structure_valid`) / `total_cases`
- `allergy_safety_rate` = sum(`allergy_safe`) / relevant allergy-constrained cases
- `preference_satisfaction_rate` = sum(`preference_satisfied`) / relevant preference-constrained cases
- `average_ingredient_coverage` = average of `ingredient_coverage_score`
- `average_additional_ingredients` = average of `additional_ingredient_count`
- `average_practical_quality` = average of `practical_quality_score`

## OCR Metrics

Using `ocr-evaluation-results.csv`:

- `ocr_success_rate` = count of successful OCR runs / total images
- `structured_output_success_rate` = count where JSON-style nutrition output is produced / total images
- `calories_exact_match_rate` = sum(`calories_correct`) / total successful outputs
- `macro_exact_match_rate`
  - use protein, carbs, fat
  - formula = (`protein_correct` + `carbs_correct` + `fat_correct`) / (3 * total successful outputs)
- `average_correct_fields_per_image` = average of `correct_field_count`
- `high_quality_extraction_rate` = percentage of images with `correct_field_count >= 5`

## Error Analysis Suggestions

Group failures into:

- input quality problems
- OCR reading problems
- numeric parsing problems
- structuring / field-mapping problems
- safety / dietary-constraint problems


