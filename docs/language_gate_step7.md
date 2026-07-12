# Language Gate Step 7

Input: `data/all_greenhouse_jobs_from_targets.jsonl`

## Counts
- rows_total: 84487
- invalid_rows: 0
- rows_en: 81011 (95.89%)
- rows_non_en: 3118 (3.69%)
- rows_unknown: 358 (0.42%)

## Output Files
- en: `data/jobs/jobs_en_filtered.jsonl`
- non_en: `data/jobs/jobs_non_en.jsonl`
- unknown: `data/jobs/jobs_unknown_language.jsonl`

## Top Reasons (en)
- hint_detector_agree: 80709
- detector_primary: 155
- hint_detector_disagree_detector_override: 94
- text_stopwords_en: 53

## Top Reasons (non_en)
- hint_detector_agree: 2739
- hint_detector_disagree_detector_override: 375
- detector_primary: 4

## Top Reasons (unknown)
- low_signal_mixed_or_ambiguous: 175
- hint_without_text_support: 166
- hint_without_enough_text: 16
- text_too_short_or_ambiguous: 1
