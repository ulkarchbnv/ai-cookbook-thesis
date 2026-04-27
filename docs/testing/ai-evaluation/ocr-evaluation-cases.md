# OCR Evaluation Cases

Use these cases to evaluate the OCR + LLM nutrition structuring pipeline.

The project currently relies on:

- image upload validation
- image preprocessing
- OCR text extraction
- LLM-based structuring into nutrition JSON

For each image, capture:

- original image screenshot
- extracted OCR text screenshot
- structured output screenshot
- whether each target field is correct

## Scoring Rules

For each case, score these fields:

- `product_name_correct`: `1` or `0`
- `serving_size_correct`: `1` or `0`
- `calories_correct`: `1` or `0`
- `protein_correct`: `1` or `0`
- `carbs_correct`: `1` or `0`
- `fat_correct`: `1` or `0`
- `sugar_correct`: `1` or `0`
- `sodium_correct`: `1` or `0`
- `fiber_correct`: `1` or `0`

If a field is not present on the real label and the system leaves it empty/null correctly, count that as correct.

## Recommended Cases

### O-01 Clear Nutrition Label

- File: `C:\Users\Admin\Downloads\nutrition-facts.jpg`
- Purpose: baseline OCR quality on a readable label
- Expected behavior:
  - OCR should succeed
  - most numeric fields should be correct

### O-02 Alternate Label Layout

- File: `C:\Users\Admin\Downloads\unnamed.jpg`
- Purpose: test layout robustness on a different label style
- Expected behavior:
  - OCR should still return structured values
  - some errors may appear if the layout is unusual

### O-03 Real-World Camera Photo

- File: `C:\Users\Admin\Downloads\WhatsApp Image 2026-04-14 at 13.56.17.jpeg`
- Purpose: test more realistic capture conditions
- Expected behavior:
  - OCR may degrade slightly
  - structured output should still recover key fields if text is readable

## Additional Cases to Add Manually

Add more images if available to make the evaluation stronger:

- angled label photo
- slightly blurry label
- partially cropped label
- low-contrast label
- failure case where no readable text should be detected

## Aggregated Metrics to Compute

- total images tested
- OCR success rate
- structured output success rate
- calories exact-match rate
- macro-field exact-match rate
- average number of correct fields per image
- percentage of images with at least 5 correct fields

## Error Analysis Prompts

For each failed or weak case, note:

- was the problem caused by image quality, OCR extraction, or LLM structuring?
- were numeric values confused with serving-size or percentage values?
- was the product name hallucinated or omitted?
- did units cause parsing problems?
