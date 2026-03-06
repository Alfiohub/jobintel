# Micro-SaaS Post-MVP Steps

Questo documento blocca i prossimi step dopo il MVP, così non perdiamo la direzione.

## Fase 1 - Data model industriale
- Estendere schema `jobs_indexed` con:
  - `salary_period` (`year|month|day|hour`)
  - `years_experience_min`
  - `education_level`
  - `field_confidence_json` (confidenza per singolo campo)
- Aggiungere tabelle dimensione:
  - `roles`, `job_posting_roles`
  - `skills`, `job_posting_skills`
  - opzionale: `industries`, `job_posting_industries`

Definition of Done:
- Migrazione DB completata
- Backfill dati minimo su subset
- API non regressa

## Fase 2 - Tassonomia controllata
- Definire tassonomia stabile:
  - `job_family` (10-20 valori)
  - `role` canonici (versione iniziale 50-150)
  - `seniority` (6-8 valori)
  - `work_mode` (3 valori)
  - `employment_type` (5-8 valori)
- Introdurre dizionario alias (`canonical_name`, `aliases[]`) per role/skills.

Definition of Done:
- Mapping attivo su pipeline
- Output sempre canonico nei campi principali

## Fase 3 - Pipeline di estrazione a cascata
- Regole ad alta precisione (override hard):
  - employment/work_mode/salary/anni esperienza
- Classificazione semantica per campi “soft”:
  - `job_family`, `role`, `seniority`, `industry`
- Soglia confidenza:
  - se `< threshold` invio a review queue

Definition of Done:
- Ogni campo critico ha confidenza
- Casi ambigui segregati in review

## Fase 4 - Human-in-the-loop
- UI minima di revisione:
  - confronto `raw vs normalized`
  - modifica rapida dei campi
  - conferma/salvataggio correzione
- Salvare le correzioni come “gold”:
  - training/eval set
  - nuove regole/alias

Definition of Done:
- Review queue operativa
- Correzioni persistite e riusabili

## Fase 5 - Metriche qualità
- Tracciare KPI:
  - `% annunci con location parsata`
  - `% con seniority assegnata`
  - `% con salary valido`
  - precision/recall su skills (campione)
  - `human_override_rate`
  - alias non riconosciuti top-N

Definition of Done:
- Dashboard o report periodico disponibile
- Soglie qualità minime definite

## Fase 6 - Costi e policy provider
- Policy runtime:
  - default `hash`
  - `openai/gemini` solo quando necessario
- Policy indexing:
  - batch + cache hash contenuto
  - no ricalcolo su duplicati

Definition of Done:
- Policy costi formalizzata
- Budget/mese stimato e monitorato

Riferimento operativo: `docs/embedding_policy.md`
