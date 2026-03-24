# NER Annotation Schema (v1)

## Allowed labels
- `ROLE`
- `SENIORITY`
- `SKILL`
- `WORKPLACE_TYPE`
- `EMPLOYMENT_TYPE`
- `LOCATION`
- `SALARY`
- `FUNCTION_FAMILY`

## Allowed source fields
- `title`
- `description_text`
- `location_raw`

## Entity object
```json
{
  "label": "SKILL",
  "text": "Python",
  "source_field": "description_text",
  "start": 120,
  "end": 126
}
```

Constraints:
- `start` inclusive, `end` exclusive
- offsets must be valid for the selected `source_field`
- empty/whitespace-only spans are invalid

## Record status values
- `todo`
- `preannotated`
- `converted`
- `openai_annotated`
- `openai_error`
