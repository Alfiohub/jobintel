# Saved Search CRUD Polish Step 31

## Obiettivo
Completare la gestione Saved Searches come CRUD operativa (update/delete), mantenendo integrazione pulita tra service, API e Admin UI.

## Operazioni supportate
- Create
- List
- Enable / Disable
- Run
- Check new
- **Update**
- **Delete**

## API endpoint nuovi
- `POST /saved-searches/{search_id}/update`
- `POST /saved-searches/{search_id}/delete`

### `POST /saved-searches/{search_id}/update`
Payload minimo:
- `name`
- `query_type` (`filters` | `pack`)
- `is_enabled`
- `filters_json` se `query_type=filters`
- `pack_name` se `query_type=pack`

Behavior:
- valida coerenza payload/query_type
- aggiorna record saved search
- preserva modello e metadati esistenti

### `POST /saved-searches/{search_id}/delete`
Behavior:
- elimina saved search
- elimina anche stato `saved_search_seen` associato

## Admin UI aggiornata
Nuove pagine/azioni:
- `GET /admin/saved-searches/{search_id}/edit`
- `POST /admin/saved-searches/{search_id}/edit`
- `POST /admin/saved-searches/{search_id}/delete`

Aggiornamenti lista:
- link `Edit` per ogni search
- azione `Delete` direttamente in tabella

## Limiti noti
- nessuna auth/multi-user
- nessun bulk edit/delete
- nessuna scheduling policy avanzata
- nessun workflow di versioning storico delle query salvate
