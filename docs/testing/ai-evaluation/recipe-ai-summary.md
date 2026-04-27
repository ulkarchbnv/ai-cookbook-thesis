# Recipe AI Evaluation Summary

Based on the twelve executed recipe-generation cases:

- Total evaluated cases: `12`
- Successful responses: `11 / 12`
- Structure validity rate: `91.7%`
- Allergy safety rate: `100%` across allergy-constrained cases
- Preference satisfaction rate: `100%` across preference-constrained cases
- Average ingredient coverage score: `0.75`
- Average additional ingredient count: `0.33`
- Average practical quality score: `4.4 / 5`

## Main observations

- Baseline cases produced complete structured outputs with good ingredient use.
- Allergy-constrained cases correctly excluded unsafe ingredients and surfaced warnings.
- Preference-conflict cases also favored rule compliance over preserving conflicting input.
- Ingredient drift was generally limited, though a few cases introduced one or two extra ingredients.
- The fully conflicting case was correctly rejected instead of generating an unsafe result.
