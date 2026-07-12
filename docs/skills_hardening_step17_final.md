# Skills Hardening Step 17 Final

## Cosa è stato cambiato
- Hardening dell'estrazione skills in `extraction/rules.py`:
  - match skill sempre valido se presente nel titolo (segnale forte).
  - su `requirements_clean`: skill accettata solo con cue testuali forti (required/experience/proficient/preferred/etc.).
  - su `description_clean` e `responsibilities_clean`: skill accettata solo con contesto locale forte attorno al match.
- `ExtractionStage` aggiornato per passare anche `requirements_clean` e `responsibilities_clean` a `extract_skills`.
- Aggiunto test negativo per mention debole (`Python community`) che non deve estrarre skill.

## Prima/Dopo (query skill-based)
- jobs_with_python_skill: 13660 -> 11252 (-2408)
- other_with_skills: 21265 -> 17265 (-4000)
- has_skills (indexed completeness): 40105 -> 32894 (-7211)

## Top skill counts dopo hardening (focus)
- python: 11252
- sql: 6654
- tableau: 2223
- dbt: 770
- figma: 0
- salesforce: 4979

## Sample query results dopo hardening
- jobs_with_python_skill (top 10):
  - https://stripe.com/jobs/search?gh_jid=7743311 | Data Writer and Editor | other | family=other | skills=['python']
  - https://stripe.com/jobs/search?gh_jid=7736640 | Head of Connect & Crypto F&S | other | family=other | skills=['python', 'sql', 'tableau', 'machine_learning']
  - https://stripe.com/jobs/search?gh_jid=7733233 | IT Support Engineer | other | family=other | skills=['python']
  - https://stripe.com/jobs/search?gh_jid=7733216 | IT Support Engineer | other | family=other | skills=['python']
  - https://stripe.com/jobs/search?gh_jid=7716032 | Staff Engineer - Production Eng | other | family=other | skills=['python', 'java']
  - https://stripe.com/jobs/search?gh_jid=7685855 | Technical Program Manager, Risk | technical_program_manager | family=program_management | skills=['python', 'sql']
  - https://stripe.com/jobs/search?gh_jid=7678655 | Technical Program Manager, Risk | technical_program_manager | family=program_management | skills=['python', 'sql']
  - https://stripe.com/jobs/search?gh_jid=7650073 | Technical Account Manager, Bridge | account_manager | family=sales | skills=['python', 'node']
  - https://stripe.com/jobs/search?gh_jid=7649036 | Processing Cost Accountant | accountant | family=finance | skills=['python', 'sql', 'tableau', 'power_bi', 'excel']
  - https://stripe.com/jobs/search?gh_jid=7646513 | AI Solutions Developer, Finance | other | family=other | skills=['python', 'sql']
- other_with_skills (top 10):
  - https://stripe.com/jobs/search?gh_jid=7748617 | Bridge Operations Associate | other | family=other | skills=['sql']
  - https://stripe.com/jobs/search?gh_jid=7743311 | Data Writer and Editor | other | family=other | skills=['python']
  - https://stripe.com/jobs/search?gh_jid=7743307 | Frontend Platform Engineer, JavaScript Infrastructure | other | family=other | skills=['javascript', 'typescript', 'react']
  - https://stripe.com/jobs/search?gh_jid=7738241 | Verifications Operations Associate | other | family=other | skills=['sql']
  - https://stripe.com/jobs/search?gh_jid=7737241 | Backend / API Engineer, Billing | other | family=other | skills=['java']
  - https://stripe.com/jobs/search?gh_jid=7737237 | Backend / API Engineer, Billing | other | family=other | skills=['java']
  - https://stripe.com/jobs/search?gh_jid=7736640 | Head of Connect & Crypto F&S | other | family=other | skills=['python', 'sql', 'tableau', 'machine_learning']
  - https://stripe.com/jobs/search?gh_jid=7736171 | SDK Engineer (React/React Native), Privy | other | family=other | skills=['react']
  - https://stripe.com/jobs/search?gh_jid=7733301 | Consumer Operations Associate | other | family=other | skills=['excel']
  - https://stripe.com/jobs/search?gh_jid=7733233 | IT Support Engineer | other | family=other | skills=['python']

## Tradeoff introdotti
- Precisione migliorata: meno skill da mention incidentali o deboli.
- Recall ridotta su alcuni annunci dove skill è presente ma non espressa con contesto forte.
- Comportamento resta deterministico e trasparente (regex/rules).

## Limiti residui
- Nessuna disambiguazione semantica: skill omonime/contesti borderline possono restare rumorosi.
- Sezioni requirements/responsibilities dipendono dalla qualità della pulizia heading-based.
- Nessun ranking/semantic re-ordering in retrieval v1.

## Riferimenti
- Debug pre-hardening: `docs/skills_quality_step17.md` / `.json`
- Report retrieval quality baseline: `docs/retrieval_quality_step16.md` / `.json`
- Indexed report aggiornato: `docs/indexed_job_stage_step14.md` / `.json`