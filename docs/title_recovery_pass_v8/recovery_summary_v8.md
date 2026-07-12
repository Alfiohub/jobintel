# Title Coverage Recovery Pass v8 — Normalization Context Recovery

## Scope
Pass tecnico di preprocessing/normalizzazione per recuperare contesto classificatorio perso (niente expansion ampia di nuove regole prodotto/UI).

## Before / After
- Total rows: `81,011`
- `other` before (v7): `41,628` (`51.39%`)
- `other` after (v8): `41,526` (`51.26%`)
- Delta `other`: `-102`

## Cosa viene preservato ora (e cosa no)

### Preservato (solo segnali ad alta utilità)
Dal contenuto tra parentesi vengono mantenuti in normalizzazione solo token whitelisted:
- `retail`
- `store`
- `floor`
- `mechanic`
- `pump`
- `power`
- `hvac`
- `automotive`
- `parts`

### Non preservato (noise)
Resta rimosso il rumore non classificatorio, ad esempio:
- `part-time`
- `remote`
- sigle geografiche / location-like (`emea`, ecc.)

## Esempi di normalizzazione (v8)
- `Stylist (Retail) (Part-time)` -> `stylist retail`
- `Floor Lead (Retail) (Part-time)` -> `floor lead retail`
- `Field Technician (Mechanic) (Pump, Power & HVAC)` -> `field technician mechanic pump power hvac`
- `Inside Sales Representative (Remote) (EMEA)` -> `inside sales representative`

## Cluster sbloccati dal preprocessing
1. **Retail contextual recovery**
- `Stylist (Retail) (Part-time)` ora mappabile con contesto retail: `27` match (`store_associate`)
- `Floor Lead (Retail) (Part-time)` ora mappabile con contesto retail: `25` match (`store_associate`)

2. **Industrial contextual recovery**
- `Field Technician (Mechanic) (Pump, Power & HVAC)` ora non resta in `other`: `20` match (`field_technician`)

## Top residual `other` (post-v8)
1. `general manager` (40)
2. `senior market strategy and partnerships manager` (36)
3. `hair color bar assistant, licensed cosmetologist` (32)
4. `general application` (31)
5. `producer` (27)
6. `social enterprise and program delivery-evergreen` (27)
7. `personal care specialist (part time)` (26)
8. `senior systems engineer` (25)
9. `quantitative researcher` (24)
10. `senior network engineer` (23)
11. `network engineer` (22)
12. `business analyst` (20)
13. `board certified behavior analyst` (20)
14. `solution specialist` (20)
15. `sonder responder` (19)
16. `restaurant general manager` (19)
17. `story desk editor` (19)
18. `manager, software engineering` (18)
19. `systems engineer` (18)
20. `cultivation associate` (18)

## Test / guardrail
Suite titles eseguita:
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Risultato: `23 passed`

Aggiunti test specifici su normalizzazione contestuale per verificare:
- recupero token utili tra parentesi
- esclusione di noise non classificatorio

## Cluster consigliato per pass successivo (v9)
1. **Residual engineering ambiguity** (`systems/network`) con regole precision-only dedicate
2. **Generic managerial/program titles** (`general manager`, `program/strategy evergreen`) con guardrail forti
3. **Healthcare residual precision** (`board certified behavior analyst`, `personal care specialist`) senza mapping larghi
