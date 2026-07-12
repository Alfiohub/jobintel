# Gold Eval Annotation Schema (v1)

Questo file definisce come compilare `docs/gold_eval_set_v1.csv` per la valutazione manuale.

## Scope
- title normalization quality
- role family quality
- experience extraction quality
- education extraction quality
- soft skills (lista controllata, facoltativa in v1)
- location/country quality
- seniority and employment type quality
- salary extraction quality (se presente)

## Label Columns
- `gold_normalized_title`:
  - valore canonicale atteso (es. `data_engineer`, `product_manager`)
- `gold_role_family`:
  - famiglia attesa (es. `data_engineering`, `product_management`, `sales`)
- `gold_experience_years_min`:
  - intero minimo anni richiesti; vuoto se non specificato
- `gold_experience_years_max`:
  - intero massimo anni richiesti; vuoto se non specificato
- `gold_experience_required`:
  - `1` se esplicitamente richiesti anni di esperienza
  - `0` se non richiesto/solo preferibile
  - vuoto se ambiguo
- `gold_education_level`:
  - valori ammessi: `none`, `high_school`, `bachelor`, `master`, `phd`, `unspecified`
- `gold_degree_required`:
  - `1` se degree richiesto
  - `0` se preferred/equivalent experience
  - vuoto se non chiaro
- `gold_soft_skills`:
  - lista separata da `;` con taxonomy ridotta
  - v1 consigliata: `communication;teamwork;leadership;problem_solving;adaptability;stakeholder_management;attention_to_detail;time_management`
- `gold_location_type`:
  - valori ammessi: `remote`, `hybrid`, `onsite`, `unspecified`
  - vuoto se non deducibile
- `gold_country`:
  - nome paese (es. `Italy`) o ISO-2 (es. `IT`)
  - vuoto se non deducibile
- `gold_location_city`:
  - città della sede principale dell'annuncio
  - vuoto se non deducibile
- `gold_employment_type`:
  - valori ammessi: `full_time`, `part_time`, `contract`, `internship`, `temporary`, `unspecified`
- `gold_seniority`:
  - valori ammessi: `intern`, `junior`, `mid`, `senior`, `lead`, `manager`, `director`, `executive`, `unspecified`
- `gold_language_requirements`:
  - lista separata da `;` (es. `english;italian`)
  - vuoto se non deducibile
- `gold_salary_min` / `gold_salary_max`:
  - numeri interi (senza separatori)
  - vuoto se non deducibile
- `gold_salary_currency`:
  - preferire ISO-3 (es. `USD`, `EUR`, `GBP`)
  - vuoto se non deducibile
- `gold_salary_period`:
  - valori ammessi: `hourly`, `daily`, `weekly`, `monthly`, `yearly`, `unspecified`
- `gold_tools_tech`:
  - lista canonica separata da `;` (es. `python;sql;aws`)
  - vuoto se non deducibile

## QA Columns
- `labeler`: iniziali o username annotatore
- `review_status`:
  - `todo` | `in_review` | `approved`
- `notes`: razionale in caso ambiguo

## Annotation Rules
- Usa `description_clean_excerpt` + `title_clean`; se ambiguo, apri `url`.
- Se manca evidenza esplicita, lascia campo vuoto (non inventare).
- Mantieni coerenza: stesso pattern testuale => stesso label.
- In caso conflitto tra `title_raw` e body, prevale il ruolo espresso nel body solo se chiaramente dominante.

## Target Dataset
- dimensione raccomandata: `700-800` righe
- stratificazione per `role_family` con almeno 1 campione per famiglia presente
- campionamento riproducibile via seed (`build_gold_eval_set.py --seed`)
