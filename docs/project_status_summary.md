# Project Status Summary — Job Title Normalization

## 1. Scopo Finale
Lo scopo finale del progetto e costruire una pipeline di job title normalization:
- ad alta precisione
- tassonomicamente coerente
- utile ai sistemi downstream
- sostenibile da mantenere nel tempo

In termini pratici, il sistema deve prendere titoli grezzi e rumorosi e produrre:
- `normalized_title`
- `role_family`
- `classification_status`
- un output spiegabile e auditabile

Il fine vero non e abbassare `other` a tutti i costi.  
Il fine vero e potersi fidare del dato normalizzato.

## 2. Scopi Intermedi
Per arrivare allo scopo finale, il progetto e stato strutturato in obiettivi intermedi:

1. costruire un classifier ufficiale rule-based leggibile e testabile
2. ridurre `other` con batch piccoli e sicuri
3. analizzare il residuo in modo sistematico, non manuale titolo per titolo
4. usare ESCO e O*NET come knowledge layer di supporto
5. costruire un semantic layer shadow-only per retrieval e review
6. ripulire i mismatch tassonomici che falsavano i candidati interni
7. usare il contesto del job ad per i titoli che non si risolvono col solo titolo
8. formalizzare criteri di qualita e Definition of Done

## 3. Dati Usati

### 3.1 Dataset interni principali
- benchmark ufficiale piu recente: `data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl`
- righe totali attese: `81,011`
- baseline ufficiale corrente `other`: `35,952`

Dataset storici/versionati usati nel percorso:
- `data/jobs/jobs_titled_en_recovery_v46.jsonl`
- `data/jobs/jobs_titled_en_recovery_v48_safe.jsonl`
- `data/jobs/jobs_titled_en_recovery_v49_safe.jsonl`
- `data/jobs/jobs_titled_en_recovery_v50_safe.jsonl`
- `data/jobs/jobs_titled_en_recovery_v51_safe.jsonl`
- `data/jobs/jobs_titled_en_recovery_v53_safe.jsonl`
- `data/jobs/jobs_titled_en_recovery_v54_semantic_patch.jsonl`
- `data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl`

### 3.2 Dati contesto annuncio
Per il layer ibrido `title + context` abbiamo usato anche i JSON estesi degli annunci:
- `data/jobs/jobs_extracted_en.jsonl`

Campi contestuali usati:
- `description_clean`
- `requirements_clean`
- `responsibilities_clean`
- `departments_raw`
- `skills`
- `seniority`
- `employment_type`
- `tags`

### 3.3 Knowledge layer esterno

#### ESCO
Usato come supporto di discovery e review:
- `occupations_en.csv`
- `broaderRelationsOccPillar_en.csv`
- `ISCOGroups_en.csv`
- `occupationSkillRelations_en.csv`

#### O*NET
Usato come supporto di discovery e review:
- `Occupation Data`
- `Alternate Titles`
- `Related Occupations`

Nota importante:
ESCO e O*NET non sono stati usati come auto-mapper di produzione.  
Sono stati usati come supporto per candidate discovery, ranking e verifica semantica.

## 4. Metodologia Usata
La metodologia del progetto e stata volutamente stratificata.

### 4.1 Layer 1 — Motore ufficiale rule-based
Il motore ufficiale resta il source of truth di produzione.

Caratteristiche:
- regole strette
- guardrail anti-overmatch
- test positivi e negativi
- eval completo su benchmark versionato

Principio:
- meglio lasciare `other` che classificare male

### 4.2 Layer 2 — Residual analysis
Il residuo `other` e stato trattato come backlog operativo.

Metodi usati:
- frequency analysis
- normalized residual strings
- token analysis
- bigram / trigram analysis
- fuzzy / lexical clustering

Obiettivo:
- capire quali cluster veri restano
- separare cluster promuovibili, cluster ambigui e rumore

### 4.3 Layer 3 — Shadow discovery con ESCO/O*NET
E stata costruita una pipeline parallela shadow per:
- candidate generation
- ranking di cluster residui
- supporto semantico esterno
- shortlist di cluster ad alto ROI

Questa parte non ha sostituito la produzione.
Ha funzionato come discovery e reviewer layer.

### 4.4 Layer 4 — Semantic layer bootstrap
E stato costruito un semantic layer separato sotto:
- `experiments/title_semantic_layer/`

Funzioni principali:
- corpus interno dei canonical titles
- indice ESCO
- indice O*NET
- semantic-lite retrieval
- candidate ranking
- reviewer report

Approccio usato:
- retrieval trasparente
- semantic-lite locale
- niente black box di produzione

### 4.5 Layer 5 — Taxonomy governance
E stata fatta una review mirata dei taxonomy gap per distinguere:
- vero gap tassonomico
- ambiguita title-only
- casi che richiedono contesto
- casi da lasciare in `other`

Decisioni usate:
- `map_to_existing_label`
- `new_label_worth_adding`
- `keep_other_by_policy`
- `needs_context_not_title_only`
- `taxonomy_merge_or_cleanup_needed`

### 4.6 Layer 6 — Hybrid title + context
Per i titoli ancora ambigui dopo tutto il lavoro title-only, e stato aperto un layer ibrido:
- `title + context`

Questo layer:
- non sostituisce il classifier ufficiale
- si attiva solo dopo `classification_status == other`
- usa il testo del job ad per disambiguare
- resta leggibile, auditabile e shadow-first

## 5. Cosa Abbiamo Fatto Finora

### Capitolo 1 — Fondazione del sistema
Fatto:
- definito il contratto minimo del sistema
- fissato benchmark e logica before/after

### Capitolo 2 — Safe recovery rule-based
Fatto:
- recovery pass iterativi
- test e eval continui
- riduzione progressiva di `other` con patch conservative

### Capitolo 3 — Shadow discovery layer
Fatto:
- clustering lessicale del residuo
- discovery guidata da ESCO/O*NET
- ranking dei cluster piu promettenti

### Capitolo 4 — Safe adoption da shadow
Fatto:
- promozione solo di cluster low-risk / medium-low
- stop quando il ROI e sceso

### Capitolo 5 — Semantic layer bootstrap
Fatto:
- corpus interni + ESCO + O*NET
- retrieval e ranking shadow-only
- reviewer layer semantico

### Capitolo 6 — Semantic reviewer
Fatto:
- reviewer scoring trasparente
- shortlist di candidati sicuri / semi-sicuri
- failure modes espliciti

### Capitolo 7 — Taxonomy gap review
Fatto:
- inventory dei taxonomy gap
- distinzione tra gap reale e ambiguita intrinseca

### Capitolo 8 — Targeted taxonomy cleanup
Fatto:
- cleanup semantico mirato nel solo semantic layer
- remap confermati:
  - `software_development_manager -> engineering_manager`
  - `production_engineer -> manufacturing_engineer`
  - `fpga_engineer -> electrical_engineer`
  - `it_administrator -> it_support_specialist`
  - `technical_architect -> solutions_architect`
- valutazione separata di `data_science_manager`

### Capitolo 9 — Production promotion planning
Fatto:
- traduzione del cleanup in candidate patch ufficiale
- defer esplicito di `data_science_manager`

### Capitolo 10 — Next semantic-assisted safe batch
Fatto:
- batch ufficiale successivo guidato dal reviewer
- nuovo abbassamento di `other`

### Capitolo 11 — Hybrid title + context design
Fatto:
- design del context layer
- context joiner shadow-only
- scoring contestuale
- proposal di regole context-gated
- tuning shadow
- formal review finale

Risultato:
- due candidati contestuali pronti per review di patch:
  - `Onboarding Specialist -> customer_success_manager`
  - `Producer -> content_producer`

### Capitolo 12 — Definition of Done
Fatto:
- soglia minima di precisione auditata
- soglia massima di overmatch
- target realistico di `other`
- policy ufficiale per `keep_other`
- workflow di manutenzione
- governance nuove label

## 6. Risultati Principali Finora

### 6.1 Stato del benchmark ufficiale
Nel benchmark ufficiale corrente:
- dataset: `data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl`
- `rows_total`: `81,011`
- `matched`: `45,059`
- `other`: `35,952`

### 6.2 Stato del pilot ibrido shadow
Nel pilot shadow context-gated piu recente:
- dataset shadow: `data/jobs/jobs_titled_en_recovery_v56_context_shadow_v2.jsonl`
- delta shadow su `other`: `-37`
- match context-gated:
  - `Onboarding Specialist`: `11`
  - `Producer`: `26`

### 6.3 Decisioni architetturali ormai fissate
- produzione ufficiale: rule-based
- semantic layer: reviewer/ranker, non auto-classifier
- ESCO/O*NET: supporto di discovery e validazione
- context layer: solo per casi ambigui dopo il pass title-only
- `keep_other`: scelta di qualita legittima

## 7. Stato Attuale del Sistema
Tutti i 12 capitoli della roadmap sono stati chiusi.

Questo significa che:
- l’architettura principale e stata costruita
- la metodologia di lavoro e stata stabilizzata
- le soglie di qualita sono state definite
- il progetto e passato dalla fase di costruzione alla fase di manutenzione controllata

## 8. Cosa Non Stiamo Facendo
Il progetto non sta cercando di:
- eliminare `other` a ogni costo
- fare semantic auto-mapping opaco
- introdurre regex larghe e incontrollate
- espandere la taxonomy senza governance
- classificare tutto anche quando il titolo e ambiguo

## 9. Stato Corretto del Progetto Oggi
Il progetto oggi e in questa fase:

### fase chiusa
- build-out dell’architettura
- stabilizzazione della metodologia
- apertura del semantic reviewer
- apertura del context layer

### fase corrente
- manutenzione controllata del sistema
- promozione solo di patch piccole, spiegabili e auditate
- possibile review di produzione per i due gate contestuali:
  - `Onboarding Specialist`
  - `Producer`

## 10. Prossimi Passi Naturali
I prossimi passi corretti non sono una riscrittura del sistema.
Sono:

1. decidere se promuovere i due gate contestuali candidati in produzione
2. continuare con batch piccoli solo se superano audit e guardrail
3. lasciare in `other` i cluster senza segnale stabile o senza contesto sufficiente
4. usare il workflow standard definito nella Definition of Done per tutta la manutenzione futura

## 11. Riferimenti Principali
- roadmap generale: [roadmap_capitoli](/home/afio/Documenti/Code/Python_code/Jinaj/joballert2/roadmap_capitoli)
- definition of done: [phase_e6_definition_of_done.md](/home/afio/Documenti/Code/Python_code/Jinaj/joballert2/docs/phase_e6_definition_of_done.md)
- piano promozione produzione: [phase_e4_production_promotion_plan.md](/home/afio/Documenti/Code/Python_code/Jinaj/joballert2/docs/phase_e4_production_promotion_plan.md)
- review formale regole contestuali: [phase_e5_formal_review_context_rules_v1.md](/home/afio/Documenti/Code/Python_code/Jinaj/joballert2/docs/phase_e5_formal_review_context_rules_v1.md)
- eval benchmark ufficiale corrente: [title_eval_step13.md](/home/afio/Documenti/Code/Python_code/Jinaj/joballert2/docs/title_recovery_pass_v55_semantic_batch/title_eval_step13.md)
