# Daily/Weekly Ops Polish v1 (Step 79)

## Obiettivo
Rendere più lineare il workflow operativo quotidiano e settimanale, armonizzando Today, Review, Notifications e Saved Searches senza introdurre nuove feature grosse.

## Cambiamenti UX applicati

### 1) Distinzione chiara tra viste operative
- **Today**: lavoro immediato (azioni del giorno).
- **Review**: manutenzione periodica (backlog/pipeline/search cleanup).
- **Notifications**: segnali/attenzione da smistare verso Today o Review.
- **Saved Searches**: strategia, coverage, hygiene e lifecycle del portfolio.

Questa distinzione è ora esplicitata in header/testi delle pagine, non solo implicita nella navigazione.

### 2) Dashboard `/admin` con guida operativa leggera
Aggiunto blocco sintetico con:
- **Daily workflow** (Today, inbox, shortlist follow-up)
- **Weekly maintenance** (Review, Saved Searches, Notifications)

Effetto: onboarding operativo più rapido su “cosa fare oggi” vs “cosa mantenere periodicamente”.

### 3) Today `/admin/today`
Miglioramenti:
- testo guida esplicito: *Today = immediate action*
- CTA cross-view:
  - `Open weekly review`
  - `Open saved searches strategy`
- empty states più orientati al prossimo passo (inbox/saved searches/review)

### 4) Review `/admin/review`
Miglioramenti:
- testo guida esplicito: *Weekly maintenance focus*
- CTA operative verso:
  - Today
  - Notifications
  - Saved Searches (active/archived)

### 5) Notifications `/admin/notifications`
Miglioramenti:
- testo guida: pagina segnali, esecuzione in Today, manutenzione in Review
- CTA cross-view:
  - `Open Today view`
  - `Open Review view`
  - `Open Saved Searches`
- empty state più chiaro su cosa controllare comunque

### 6) Saved Searches `/admin/saved-searches`
Miglioramenti:
- blocco guida: *Search operations model: strategy + hygiene + lifecycle*
- cross-links rapidi verso Today/Review/Notifications
- helper testuale quando filtro `archived` è attivo (storico/reference, fuori dal working set)

## Workflow consigliato (quotidiano/settimanale)
1. **Ogni giorno**: apri `/admin/today`, chiudi follow-up e shortlist items critici.
2. **Durante il giorno**: usa `/admin/notifications` come inbox segnali e apri la superficie corretta.
3. **Ogni settimana**: apri `/admin/review` per backlog pipeline e manutenzione candidature.
4. **Manutenzione portfolio**: passa da `/admin/saved-searches` per coverage/hygiene/lifecycle.

## Test aggiornati
- `tests/api/test_admin_ui_step30.py`
  - presenza testi guida (`Daily workflow`, `Weekly maintenance`, `Today = immediate action`, `Weekly maintenance focus`, `Signals view`)
  - presenza CTA/link principali tra viste
  - coerenza navigazione operativa e blocco guidance in saved searches

## Limiti noti
- nessuna nuova capability AI/recommendation
- nessun calendar sync/reminder avanzato
- nessuna analytics avanzata aggiuntiva
- polish focalizzato su chiarezza UX e navigazione tra superfici esistenti
