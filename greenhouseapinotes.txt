# Greenhouse API Notes

## Scopo

Questo file serve come riferimento stabile per ricordare **cosa otteniamo oggi dalle API Greenhouse**, come quei dati entrano nella pipeline, e quali campi sono utili per i moduli futuri.

Va letto come documento di supporto per:

* ingestion
* canonicalization
* language detection
* cleaning
* extraction
* title normalization
* estensione futura ad altri ATS

---

## Fonte attuale

Endpoint principale usato oggi:

* `GET https://boards-api.greenhouse.io/v1/boards/{board}/jobs`
* con parametro opzionale `content=true`

Questo endpoint restituisce una lista di job pubblici della board.

---

## Cosa otteniamo davvero da Greenhouse

Per ogni job otteniamo almeno questi campi utili.

### Identità annuncio

* `id`
* `absolute_url`
* `internal_job_id`
* `requisition_id`

Uso:

* identificazione record
* deduplica
* tracking aggiornamenti

### Titolo

* `title`

Uso:

* title cleaning
* title normalization
* role family classification

### Azienda

* `company_name`

Uso:

* presentazione
* filtri
* canonical raw job

### Lingua

* `language`

Uso:

* `language_hint`
* primo segnale per language detection

Nota: non va trattato come verità assoluta senza verifica, ma è un segnale forte.

### URL annuncio

* `absolute_url`

Uso:

* chiave stabile
* identificatore funzionale dell’annuncio
* serving e linking

### Location

* `location.name`
* `offices[]`

Uso:

* `location_raw`
* location normalization futura
* remote/hybrid/onsite hints
* country/region/city inference

### Dipartimenti

* `departments[]`

Uso:

* segnale di dominio
* supporto per classification/ranking
* possibile metadata di business

### Date

* `updated_at`
* `first_published`

Uso:

* `updated_at`: ultima modifica del job
* `first_published`: vera pubblicazione iniziale

Nota importante:
non dobbiamo schiacciare tutto in un generico `posted_at` se vogliamo mantenere semantica corretta.

### Contenuto completo annuncio

* `content`

Uso:

* language detection sul raw posting
* cleaning HTML
* extraction di:

  * salary
  * skills
  * seniority hints
  * education
  * experience
  * employment type
  * domain clues

Nota importante:
`content` arriva HTML-escaped, quindi prima va:

1. unescaped
2. stripped dai tag
3. normalizzato

### Metadata aggiuntivi

* `metadata`
* `data_compliance`

Uso:

* oggi secondario
* utile per estensioni future e auditing

---

## Contratto interno consigliato (derivato da Greenhouse)

Greenhouse è una sorgente esterna. Non deve definire direttamente il dominio interno.

Da Greenhouse dobbiamo derivare almeno un `CanonicalRawJob` con questi campi:

* `source`
* `source_org`
* `external_id`
* `url`
* `title`
* `company_name`
* `location_raw`
* `published_at`
* `updated_at`
* `language_hint`
* `description_raw`
* `departments_raw`
* `offices_raw`
* `raw_payload`

---

## Come usare questi dati nella pipeline

### 1. Ingestion

Greenhouse -> `SourceRawJob`

### 2. Canonicalization

`SourceRawJob` -> `CanonicalRawJob`

### 3. Language detection

Usare:

* `language_hint`
* `title`
* excerpt di `description_raw`

### 4. Cleaning

Usare soprattutto:

* `title`
* `description_raw`
* `location_raw`

### 5. Extraction

Usare soprattutto:

* `description_raw` pulito
* `departments_raw`
* `offices_raw`

### 6. Title normalization

Usare soprattutto:

* `title_clean`
* eventuali segnali secondari di contesto se previsti più avanti

---

## Limiti attuali da ricordare

* alcune board possono essere incomplete o incoerenti
* `language` può essere presente ma non sempre abbastanza affidabile da solo
* `content` è rumoroso se non viene ripulito
* `company_name` non va derivato dal solo board token se il payload fornisce un valore migliore
* `updated_at` e `first_published` vanno distinti

---

## Regola architetturale importante

Quando aggiungeremo altri ATS:

* non dobbiamo piegare il dominio interno a Greenhouse
* ogni ATS deve avere:

  * client
  * mapper
  * collector
* tutti devono convergere nello stesso `CanonicalRawJob`

Quindi Greenhouse va trattato come:

* **adapter sorgente**, non come modello del sistema.

---

## Checklist futura quando aggiungiamo un nuovo ATS

Per ogni nuovo ATS chiedersi subito:

1. Quali identificatori espone?
2. Espone URL pubblico?
3. Espone titolo pulito?
4. Espone lingua?
5. Espone descrizione completa?
6. Espone location strutturata o solo raw?
7. Espone dipartimenti/team?
8. Espone date separate di pubblicazione e update?
9. Ci sono campi custom utili?
10. Come mappiamo tutto in `CanonicalRawJob` senza rompere i contratti interni?

---

## Sintesi

Da Greenhouse oggi otteniamo già abbastanza per costruire bene:

* ingestion
* canonical raw layer
* language gating serio
* cleaning serio
* extraction seria
* title classification

Il punto chiave non è ottenere più dati, ma **mappare bene quelli che abbiamo** dentro un contratto interno stabile.
