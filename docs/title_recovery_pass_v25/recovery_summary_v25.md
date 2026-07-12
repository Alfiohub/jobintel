# Title Coverage Recovery Pass v25 — Education Edge Expansion

## Cluster scelto
`education` edge (school counselor/director/support con pattern stretti).

## Before / After
- `other` before (v24): `39,388` (`48.62%`)
- `other` after (v25): `39,364` (`48.59%`)
- Delta `other`: `-24`

## Nuove label introdotte
- `school_counselor` -> `education`
- `school_administrator` -> `education`

## Regole aggiunte
- `education_school_counselor_edge`
- `education_school_administration_edge`
- `education_assistant_spanish_teacher_edge`

## Coverage (nuove regole)
- totale nuovi match v25: `24`
  - school counselor edge: `6`
  - school administration edge: `15`
  - assistant spanish teacher edge: `3`

## Sample titoli coperti
- `School Director` (`6`)
- `School Leadership` (`5`)
- `School Office Manager - SY 26-27` (`3`)
- `School Counselor` (`2`)
- `Virtual School Counselor - SY 26-27` (`2`)
- `Assistant Spanish Teacher` (`3`)

## Guardrail / limiti
- nessun mapping generico di tutti `counselor`/`director`
- regole ancorate a contesto esplicito `school`
- esclusi nei test pattern ambigui (`Counselor`, `Technical Instructor`, `Director of Revenue (Education...)`)

## Top residual `other` (post-v25)
1. `general manager` (40)
2. `senior market strategy and partnerships manager` (36)
3. `hair color bar assistant, licensed cosmetologist` (32)
4. `general application` (31)
5. `producer` (27)
