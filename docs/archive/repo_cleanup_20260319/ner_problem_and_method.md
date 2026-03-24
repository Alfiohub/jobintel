# NER: Problema, Strategia e Motivazioni

## Contesto

L'obiettivo del progetto non e' semplicemente classificare annunci di lavoro, ma estrarre in modo strutturato entita' utili dal testo libero dei job post, in particolare:

- `ROLE`
- `SENIORITY`
- `SKILL`
- `WORKPLACE_TYPE`
- `EMPLOYMENT_TYPE`
- `LOCATION`
- `SALARY`
- `FUNCTION_FAMILY`

Queste entita' servono poi al prodotto per:

- filtrare meglio gli annunci
- fare ranking e matching
- migliorare raccomandazioni e notifiche
- costruire dati strutturati a partire da testo non strutturato

## Problema Reale

Il problema principale emerso finora non e' uno solo. E' la combinazione di quattro fattori.

### 1. Il dataset attuale e' piccolo rispetto al corpus totale

Abbiamo a disposizione un corpus molto piu' grande di annunci, ma il training NER attuale si basa solo su circa 1.5k esempi annotati/preannotati.

Questo significa che stiamo cercando di allenare un modello su una porzione troppo ridotta del materiale disponibile.

### 2. Le label sono sbilanciate

Nel dataset attuale la label piu' presente e' `LOCATION`.

Abbiamo invece poca copertura per le label che danno piu' valore al prodotto:

- `SKILL`
- `ROLE`
- `FUNCTION_FAMILY`
- `WORKPLACE_TYPE`
- `EMPLOYMENT_TYPE`
- `SALARY`

Risultato: il modello vede tanti token `O` e poche supervisioni utili.

### 3. Le annotazioni sono deboli o incomplete

Molti record contengono poche entita', spesso solo `LOCATION` e a volte `SENIORITY`.

Questo non implica che gli annunci non contengano altre informazioni utili; implica piuttosto che il dataset di training non le sta catturando bene in modo consistente.

### 4. Il corpus e' eterogeneo

Gli annunci arrivano da:

- ATS diversi (`greenhouse`, `smartrecruiters`, `lever`)
- lingue diverse
- strutture testuali diverse

Questa variabilita' rende piu' difficile capire se il problema e':

- il dataset
- il modello
- la pipeline di training

## Cosa Abbiamo Verificato

### Baseline interno

Abbiamo costruito un baseline usando solo dati interni:

- `data/ner/train_preannotated_backfilled.jsonl`
- `data/ner/valid_preannotated_backfilled.jsonl`

Da questi e' stato creato:

- `data/ner/pipeline_internal_baseline/merged.jsonl`
- `data/ner/pipeline_internal_baseline/split/train.jsonl`
- `data/ner/pipeline_internal_baseline/split/valid.jsonl`
- `data/ner/pipeline_internal_baseline/split/test.jsonl`

### Primo training baseline

Il primo training Colab ha mostrato un problema chiaro:

- `eval_accuracy = 1.0`
- `eval_f1 = 0.0`
- `eval_precision = 0.0`
- `eval_recall = 0.0`

Interpretazione:

- il modello stava predicendo quasi solo `O`
- quindi non stava imparando entita' utili

### Problema tecnico corretto

Nel file `automation/legacy_ner/train_ner_baseline.py` l'ordine del testo combinato era:

1. `title`
2. `description_text`
3. `location_raw`

Con `max_length=512`, molte entita' presenti in `location_raw` venivano troncate.

Questo e' stato corretto portando l'ordine a:

1. `title`
2. `location_raw`
3. `description_text`

Questa correzione migliora la visibilita' delle entita', ma da sola non risolve il problema di fondo del dataset.

## Diagnosi

La diagnosi corretta e' questa:

- non e' solo un problema di modello
- non e' solo un problema di codice
- non e' solo un problema di annunci poco informativi

Il collo di bottiglia principale e' la **qualita' e densita' supervisionale del dataset NER**.

In pratica:

- i dati utili nel corpus esistono
- ma il training attuale ne cattura troppo pochi
- e li cattura in modo troppo sbilanciato

## Strategia Scelta

La strategia scelta e':

1. usare solo dati interni
2. evitare annotazione manuale
3. evitare OpenAI come annotatore di massa
4. partire con subset piu' omogenei
5. costruire gradualmente un dataset piu' denso di entita'

## Metodologia Operativa

### Fase 1: Debug con subset omogenei

Per ridurre il rumore abbiamo deciso di creare subset piu' controllati, ad esempio:

- `English-only`
- `Greenhouse-only`
- oppure `English-only + Greenhouse`

Motivazione:

- meno variabilita' strutturale
- meno rumore linguistico
- piu' facilita' nel capire se il training pipeline regge

E' stato quindi creato anche un subset:

- `data/ner/pipeline_greenhouse_en/merged.jsonl`
- `data/ner/pipeline_greenhouse_en/split/train.jsonl`
- `data/ner/pipeline_greenhouse_en/split/valid.jsonl`
- `data/ner/pipeline_greenhouse_en/split/test.jsonl`

Questo subset non risolve ancora il problema della poverta' delle label, ma e' utile per debugging piu' rigoroso.

### Fase 2: Migliorare la densita' delle label

Dato che il corpus totale e' molto piu' grande del dataset annotato, la direzione corretta non e' annotare tutto, ma selezionare esempi ad alta probabilita' di contenere entita' utili.

Approccio:

- mining dei job piu' ricchi
- weak labeling con regole e dizionari
- focus su label ad alto valore

Le label prioritarie da aumentare sono:

- `ROLE`
- `SKILL`
- `SENIORITY`
- `WORKPLACE_TYPE`
- `EMPLOYMENT_TYPE`
- `SALARY`

### Fase 3: Baseline locale e iterazione

Il ciclo scelto e':

1. costruire subset piu' puliti
2. allenare baseline piccoli ma interpretabili
3. misurare distribuzione e copertura label
4. migliorare il weak labeling
5. costruire un `train_v2` piu' denso
6. retrain

## Perche' non usare subito OpenAI

OpenAI puo' aiutare, ma non e' la strategia principale per questi motivi:

- costo elevato su grandi volumi
- qualita' non sempre coerente
- rischio di spendere molto su dati poco informativi

Quindi l'uso corretto di OpenAI, se ci sara', sara' solo:

- su casi ambigui
- su subset piccoli
- come fallback, non come pipeline principale

## Perche' non partire subito multilingua full-corpus

Allenare subito su tutto il corpus multilingua e multi-ATS aumenterebbe:

- rumore
- instabilita'
- difficolta' di debugging

Prima serve dimostrare che la pipeline funziona su un sottoinsieme controllato.

## Decisione Attuale

La decisione attuale e' questa:

1. mantenere il baseline interno come riferimento
2. usare subset omogenei per debugging
3. misurare bene la distribuzione delle label
4. costruire un dataset piu' denso usando il corpus grande
5. retrain solo dopo aver migliorato la qualita' supervisionale

## Sintesi

Il problema non e' semplicemente "il modello non riconosce le entita'".

Il problema e' che stiamo cercando di allenare un NER utile su un dataset:

- troppo piccolo rispetto al corpus disponibile
- troppo sbilanciato
- troppo povero sulle label piu' importanti
- troppo eterogeneo per il livello attuale di maturita' della pipeline

La metodologia scelta punta quindi a:

- ridurre il rumore
- aumentare la densita' di entita' utili
- usare prima subset controllati
- arrivare a un baseline che impari davvero qualcosa

Solo dopo ha senso scalare.
