# CanonicalRawJob - Step 4 Implementation

## Cosa è stato implementato
- `CanonicalRawJob` è ora implementato nel dominio come contratto reale:
  - `src/jobintel_next/domain/models/contracts.py`
- Il mapper Greenhouse produce direttamente `CanonicalRawJob` del dominio:
  - `src/jobintel_next/adapters/greenhouse/mapper.py`

## Mapping Greenhouse -> CanonicalRawJob
- `source` <- costante `"greenhouse"`
- `source_org` <- board slug
- `url` <- `absolute_url`
- `title` <- `title`
- `company_name` <- `company_name` payload (fallback board)
- `external_id` <- `id`
- `location_raw` <- `location.name`
- `published_at` <- `first_published` (normalizzato UTC ISO quando possibile)
- `updated_at` <- `updated_at` (normalizzato UTC ISO quando possibile)
- `language_hint` <- `language`
- `description_raw` <- `content`
- `departments_raw` <- `departments`
- `offices_raw` <- `offices`
- `raw_payload` <- payload intero preservato

## Verifiche introdotte
- test mapping Greenhouse aggiornato:
  - `tests/test_greenhouse_mapper.py`
- test dominio aggiornati con `raw_payload` obbligatorio:
  - `tests/domain/test_domain_models_step3.py`

## Cosa ancora NON fa
- nessuna language decision (`en/non_en/unknown`)
- nessun cleaning (`title_clean`, `description_clean`, hash)
- nessuna extraction (`salary`, `skills`, `location_type`, ...)
- nessuna title classification (`normalized_title`, `role_family`)

Questi restano ai prossimi step della pipeline.
