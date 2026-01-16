# Technical Specs — Step 1 (DB & Models)

## Stack
- SQLite (single-file database)
- SQLAlchemy ORM (synchronous)

## Time handling
We use `datetime.now(timezone.utc)` (not `utcnow()`) to ensure timezone-aware UTC timestamps in code helpers.

## Import convention
All internal imports use `from src.<package>...` to match the project layout and ensure IDE resolution.

## Model design (architectural decision)
### Why `properties` and `user_traits` are separate tables
We intentionally avoid a JSON/blob column on `events`. Instead, we store them as separate 1:1 tables:

- `event_properties` (`EventProperties`)
- `user_traits` (`UserTraits`)

Benefits:
- Explicit schema aligned with the known payload shape.
- Easy querying and indexing (e.g., `failure_reason`, `attempt_number`, `marketing_opt_in`).
- Keeps audit/debug views simple and consistent.

### 1:1 mapping
Each `Event` has:
- exactly 0..1 `EventProperties`
- exactly 0..1 `UserTraits`

Enforced by `unique=True` on `event_id` in both tables.

## Relationships
- `Event` 1..1 `EventProperties` (optional, cascade delete-orphan)
- `Event` 1..1 `UserTraits` (optional, cascade delete-orphan)
- `SendRequest.event_id` and `Suppression.event_id` are optional links back to `events` for audit traceability.
