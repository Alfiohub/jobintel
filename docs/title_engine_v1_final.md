# Title Engine V1 Final Baseline

## Obiettivo del title engine
Il title engine classifica il job title in una tassonomia interna stabile e utile al prodotto, con policy prudente:
- massimizzare precisione sui casi chiari
- evitare mapping aggressivi
- usare `other` quando il segnale non è sufficiente

Questo modulo è il componente di `title normalization` della nuova pipeline `jobintel_next`.

## Architettura del modulo titles (pipeline nuova)
Path: `src/jobintel_next/pipelines/titles/`

Componenti principali:
- `text_utils.py`: normalizzazione testuale base per matching.
- `variants.py`: varianti lessicali leggere (abbreviazioni/plurali frequenti).
- `location_noise.py`: rimozione rumore location semplice dal titolo.
- `rules.py`: regole esplicite e ordinate per priorità.
- `taxonomy.py`: source-of-truth interna `normalized_title -> role_family`.
- `classifier.py`: orchestrazione classificazione + taxonomy validation.
- `run.py`: stage operativo (`titles run`) su dataset.
- `eval.py`: evaluation/debug (`titles eval`) con report e cluster residuali.

Flow logico:
1. input `title_clean`
2. normalize text
3. normalize variants
4. strip location noise
5. match rules (priority order)
6. taxonomy validation
7. output `TitleClassification` (`matched` o `other`)

## Taxonomy attuale (baseline v1)
La baseline include famiglie core e label ad alta chiarezza già consolidate, tra cui:
- software/data core: `software_engineer`, `data_engineer`, `data_analyst`, `analytics_engineer`, `data_scientist`, `ml_engineer`, `devops_engineer`, `site_reliability_engineer`, `engineering_manager`
- product/design/architecture: `product_manager`, `product_designer`, `solutions_architect`
- sales/customer/marketing: `account_executive`, `account_manager`, `business_development_representative`, `sales_engineer`, `store_associate`, `customer_success_manager`, `marketing_specialist`
- finance/legal/recruiting/ops/admin: `financial_analyst`, `accountant`, `wealth_advisor`, `legal_counsel`, `technical_recruiter`, `operations_specialist`, `customer_service_specialist`, `executive_assistant`
- domain packs già introdotti in modo controllato: healthcare/logistics/skilled_trades/education/compliance (`nurse_practitioner`, `registered_nurse`, `physician`, `psychiatrist`, `psychotherapist`, `behavioral_support_specialist`, `driver`, `delivery_driver`, `technician`, `field_technician`, `mechanic`, `car_detailer`, `assistant_teacher`, `substitute_teacher`, `teacher`, `compliance_manager`, `compliance_specialist`)
- fallback: `other`

Riferimenti:
- `src/jobintel_next/pipelines/titles/taxonomy.py`
- `src/jobintel_next/pipelines/titles/rules.py`

## Policy principali
- Regole esplicite con priorità deterministica.
- Validazione obbligatoria regola/taxonomy: mapping non valido -> `other`.
- Policy conservativa: meglio `other` che mapping sbagliato.
- Niente inferenza semantica pesante nel title stage.
- Classificazione title-centric; contesto aggiuntivo usato in modo leggero.

## Stato attuale coverage
Fonte: `docs/title_eval_step13.json` (run corrente)
- `rows_total`: 81,011
- `matched`: 34,198
- `other`: 46,813

Lettura pragmatica:
- la baseline copre bene i cluster ad alto segnale e adiacenti al core prodotto
- la quota `other` è ancora ampia per scelta intenzionale (qualità > recall aggressiva)

## Cluster residui principali
Fonte: `docs/title_other_clusters_step13.json`
- `other_long_tail`: 39,916
- `skilled_trades`: 2,065
- `design_creative`: 1,381
- `healthcare_clinical`: 1,010
- `compliance_risk`: 649
- `logistics`: 513
- `education`: 470
- `retail_sales`: 397
- `customer_service`: 318
- `engineering_leadership`: 94

## Cosa resta volutamente `other`
Resta `other` tutto ciò che è:
- ambiguo (es. manager generici non distinguibili dal titolo)
- troppo specifico/long-tail per questa baseline
- non sufficientemente distinguibile senza contesto extra
- fuori dai domain pack già approvati

Esempio policy esplicita: `General Manager` resta volutamente `other`.

## Perché non usiamo ESCO/O*NET/ISCO come base primaria
Il sistema usa tassonomia interna come source-of-truth perché:
- obiettivo prodotto e query matching specifici del dominio SaaS
- necessità di controllo su precisione e policy di mapping
- differenza tra tassonomie pubbliche e segnali reali dei titoli ATS sporchi
- riduzione di over-mapping/rumore da crosswalk automatici

Le tassonomie esterne possono supportare analisi/candidate generation, ma non guidano direttamente la classificazione operativa v1.

## Governance per nuove label
Una nuova label entra solo se soddisfa tutti i criteri:
1. frequenza sufficiente nel corpus reale
2. distinguibilità dal titolo (segnale lessicale robusto)
3. utilità concreta al prodotto (search/filter/ranking/use-case)
4. non già coperta bene da label esistente

Regole operative:
- preferire estensione rules su label esistenti quando basta
- introdurre label nuove solo con test dedicati + evaluation delta
- evitare espansioni massive non cluster-driven

## Future domain packs (separati)
Possibili pacchetti futuri, da trattare uno per volta:
- `skilled_trades`
- `healthcare_clinical`
- `design_creative`
- `compliance_risk`
- `logistics`
- `education`
- `retail_sales`
- `customer_service`
- `engineering_leadership`

Ogni pack deve avere:
- scope esplicito
- lista titoli target ad alta frequenza
- patch piccola (taxonomy/rules/tests)
- valutazione prima/dopo

## Linee guida per espansioni future
- lavorare per cluster, non per singolo titolo isolato
- batch piccoli e misurabili
- mantenere separazione `cleaning -> variants -> location noise -> rules -> taxonomy validation`
- non introdurre logica opaca o non deterministica nel classifier v1
- consolidare periodicamente baseline e documentazione
