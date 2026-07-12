# Title Coverage Recovery Pass v14 — Design / Creative Expansion

## Scope
Pass focalizzato solo su `design_creative` residuale ad alto volume, con expansion pragmatica e controllata su sottocluster espliciti.

## Before / After
- Total rows: `81,011`
- `other` before (v13): `40,951` (`50.55%`)
- `other` after (v14): `40,650` (`50.18%`)
- Delta `other`: `-301`

## Design / Creative Cluster Delta
- `design_creative` residual before (v13): `1,334`
- `design_creative` residual after (v14): `1,096`
- Delta design_creative residual: `-238`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso label esistente `product_designer` (`design`) per sottocluster designer ad alta chiarezza.

## Regole aggiunte (sottocluster high-ROI)
- `design_designer_variants_explicit` -> `product_designer`
  - UX/UI variants
  - visual/graphic/web/digital/content/motion/integrated designer
  - con opzionale seniority + suffix di livello
- `design_product_design_leadership_explicit` -> `product_designer`
  - director/head/manager/senior manager/senior director/vp + `product design`
  - `product design manager|lead`

## Guardrail rispettati
- nessun mapping generico di tutti i `designer`
- nessun mapping generico di tutti i `producer`
- niente mapping generico su `design engineer`
- `brand designer` lasciato fuori per non rompere mapping già consolidato di `senior brand designer` -> `marketing_specialist`

## Coverage (nuove regole)
- `design_designer_variants_explicit`: `240` match
- `design_product_design_leadership_explicit`: `63` match
- totale nuovi match v14 (design-focused): `303`

Top titoli coperti:
- `Senior UX Designer` (`12`)
- `UX Designer` (`10`)
- `Integrated Designer` (`10`)
- `Visual Designer` (`9`)
- `Senior Motion Designer` (`9`)
- `Graphic Designer` (`9`)
- `Director, Product Design` (`8`)
- `Senior Content Designer` (`7`)

## Top residual `other` (post-v14)
1. `general manager` (40)
2. `senior market strategy and partnerships manager` (36)
3. `hair color bar assistant, licensed cosmetologist` (32)
4. `general application` (31)
5. `producer` (27)
6. `social enterprise and program delivery-evergreen` (27)
7. `personal care specialist (part time)` (26)
8. `quantitative researcher` (24)
9. `business analyst` (20)
10. `sonder responder` (19)
11. `restaurant general manager` (19)
12. `manager, software engineering` (18)
13. `cultivation associate` (18)
14. `k-5th grade teacher - sy 26-27` (17)
15. `leader in training` (17)
16. `outside sales representative - roofing` (17)
17. `data science manager` (16)
18. `principal engineer` (16)
19. `bilingual member services representative (remote, spanish speaking)` (16)
20. `intelligence operations integrator` (16)

## Design / Creative residual ancora scoperti (top)
- `Producer` (27)
- `UX Researcher` (12)
- `Designer` (11)
- `Creative Director` (11)
- `Art Director` (10)
- `Director of Product Design` (9)
- `Senior Designer` (9)
- `Creative Strategist` (9)
- `Brand Partnerships Manager` (8)
- `Design Engineer` (8)

## Cluster consigliato per v15
1. Design/creative precision follow-up su `UX Researcher` + art/creative direction (pattern stretti)
2. Generic managerial/program precision (`general manager`, strategy/program evergreen)
3. Operations/service ambiguity (`member services`, `cultivation associate`) con regole conservative

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v14/*`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `28 passed`
