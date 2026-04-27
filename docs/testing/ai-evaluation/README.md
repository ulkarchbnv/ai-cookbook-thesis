# AI Evaluation Pack

This folder contains structured evaluation sheets for the AI-specific parts of the thesis project:

- recipe generation with RAG + LLM
- OCR extraction and nutrition structuring

These files are intended for manual execution and thesis documentation.

## Files

- [recipe-evaluation-cases.md](C:\Users\Admin\Desktop\ai-cookbook-thesis\docs\testing\ai-evaluation\recipe-evaluation-cases.md)
- [recipe-evaluation-results.csv](C:\Users\Admin\Desktop\ai-cookbook-thesis\docs\testing\ai-evaluation\recipe-evaluation-results.csv)
- [ocr-evaluation-cases.md](C:\Users\Admin\Desktop\ai-cookbook-thesis\docs\testing\ai-evaluation\ocr-evaluation-cases.md)
- [ocr-evaluation-results.csv](C:\Users\Admin\Desktop\ai-cookbook-thesis\docs\testing\ai-evaluation\ocr-evaluation-results.csv)

## Recommended Metrics

### Recipe / RAG / LLM

- structure validity rate
- allergy safety rate
- preference satisfaction rate
- ingredient coverage rate
- unnecessary additional ingredient count
- average manual quality score

### OCR

- exact product-name correctness
- serving-size correctness
- calories exact-match rate
- macronutrient field correctness
- average correctly extracted numeric fields per image
- failure-case rate


1. Describe the evaluation dataset.
2. Explain the metrics and scoring rules.
3. Present the aggregated numerical results.
4. Provide error analysis with 3-5 representative failure examples.
5. State known limitations and how external API quality affects results.
