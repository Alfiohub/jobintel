# Import External NER Data

Use `scripts/import_external_ner.py` to convert external datasets to project schema.

## Supported input patterns
- `.jsonl` with one object per line
- `.json` containing either `[{...}]` or `{ "data": [{...}] }`

Entity input styles supported:
- Span style (`entities` / `spans` / `annotations` with `label,start,end`)
- Token BIO style (`tokens` + `ner_tags|tags|labels` like `B-SKILL`, `I-SKILL`, `O`)

## Basic command
```bash
uv run --active python scripts/import_external_ner.py \
  --input data/ner/external/raw/sample.jsonl \
  --output data/ner/external/converted/sample_converted.jsonl \
  --dataset-name sample_dataset
```

## Optional label mapping
If external labels differ, provide a JSON map:

`config/examples/ner_label_map_example.json`
```json
{
  "JOB_TITLE": "ROLE",
  "TECH_SKILL": "SKILL",
  "CITY": "LOCATION"
}
```

Run with mapping:
```bash
uv run --active python scripts/import_external_ner.py \
  --input data/ner/external/raw/sample.jsonl \
  --output data/ner/external/converted/sample_converted.jsonl \
  --dataset-name sample_dataset \
  --label-map config/examples/ner_label_map_example.json
```

## Output schema
Each row is exported with:
- `id, source, url, company_name, title, description_text, location_raw`
- `entities[]` in project format
- `annotation_status` (default `converted`)
- `external_meta` with provenance
